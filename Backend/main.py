import csv
import sqlite3
import sys
import requests
from requests_html import HTMLSession
from Backend.generate_heatmap import start_gen
from bs4 import BeautifulSoup
import hashlib


def create_cache_table(db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS scrape_cache (
           url TEXT PRIMARY KEY,
           etag TEXT
       )
    """)
    conn.commit()
    conn.close()

def get_cached_etag(url, db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT etag FROM scrape_cache WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def update_cached_etag(url, etag, db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO scrape_cache (url, etag) VALUES (?, ?)", (url, etag))
    conn.commit()
    conn.close()


def extract_covid_data_from_html(html_content):
    """
    Given the inner HTML content of the table, parse it and extract a list of
    tuples containing (state, test positivity, "Past 4 Weeks").
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tbody = soup.find('tbody')
    data = []
    if tbody:
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 3:
                state = cells[0].get_text(strip=True)
                positivity_text = cells[2].get_text(strip=True)
                try:
                    positivity = float(positivity_text)
                except ValueError:
                    positivity = 0.0
                data.append((state, positivity, "Past 4 Weeks"))
    else:
        print("No <tbody> found in the HTML.")
    return data

def scrape_cdc_covid_data():
    covid_url = "https://covid.cdc.gov/covid-data-tracker/#maps_positivity-4-week"

    
    current_etag = None
    try:
        head_response = requests.head(covid_url)
        current_etag = head_response.headers.get('ETag')
        cached_etag = get_cached_etag(covid_url)
        if current_etag and cached_etag == current_etag:
            return []
        else:
            print("ETag changed or not available. Proceeding with scrape.")
    except Exception as e:
        print("Error checking ETag for CDC COVID data:", e)
    
    if sys.platform.startswith("win"):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print("Error initializing WebDriver:", e)
            return []
        
        try:
            driver.get(covid_url)
            wait = WebDriverWait(driver, 15)
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        except Exception as e:
            print("Error during page load or table detection:", e)
            driver.quit()
            return []
        
        time.sleep(5)
        
        try:
            table_html = table.get_attribute("innerHTML")
        except Exception as e:
            print("Error retrieving table innerHTML:", e)
            driver.quit()
            return []
        
        covid_data = extract_covid_data_from_html(table_html)
        driver.quit()

        if current_etag:
            update_cached_etag(covid_url, current_etag)
        return covid_data
    else:
        session = HTMLSession()
        r = session.get(covid_url)
        r.html.render(sleep=3, timeout=20)
        table = r.html.find("table", first=True)
        if not table:
            print("No table found in the rendered HTML.")
            return []
        table_html = table.html
        covid_data = extract_covid_data_from_html(table_html)
        return covid_data

def compute_content_hash(content: str) -> str:
    """Compute an MD5 hash for the given content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def add_cases_to_db(db_name="health_data.db"):
    """
    Fetches the US states table from Worldometers, parses out each state name and its current new cases,
    then updates the existing COVID_Cases rows.
    In addition, it scrapes the global Deaths and Recovered numbers from the page and saves them
    as separate metrics under state "United States".
    Returns a list of (state, cases) that were processed (for the state-level cases).
    """
    worldometers_url = "https://www.worldometers.info/coronavirus/country/us/"

    session = HTMLSession()
    r = session.get(worldometers_url)
    r.html.render(sleep=3, timeout=20)

    table = r.html.find("table#usa_table_countries_today", first=True)
    if not table:
        print("No Worldometers table found.")
        return []

    current_hash = compute_content_hash(table.html)
    cached_hash = get_cached_etag(worldometers_url)
    if current_hash and cached_hash == current_hash:
        print("No change in Worldometers state-level data detected (hash unchanged).")
        state_processed = []
    else:
        soup = BeautifulSoup(table.html, "html.parser")
        rows = soup.select("tbody tr")

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        state_processed = []
        
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue

            a_tag = row.find("a", class_="mt_a")
            if a_tag and a_tag.get_text(strip=True):
                state = a_tag.get_text(strip=True)
            else:
                state = cells[1].get_text(strip=True)

            raw = cells[6].get_text(strip=True).replace(",", "")
            try:
                cases = int(raw)
            except ValueError:
                continue

            cursor.execute("""
                UPDATE state_metrics
                   SET metric_value = metric_value + ?
                 WHERE state = ? AND metric_type = 'COVID_Cases'
            """, (cases, state))
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO state_metrics
                        (state, metric_type, metric_value, year)
                    VALUES (?, 'COVID_Cases', ?, 'Current')
                """, (state, cases))
            state_processed.append((state, cases))

        conn.commit()
        conn.close()
        update_cached_etag(worldometers_url, current_hash)

    global_key = worldometers_url + "_global"
    try:
        response = requests.get(worldometers_url)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching global Worldometers stats:", e)
        return state_processed

    soup_global = BeautifulSoup(response.text, "html.parser")
    main_counters = soup_global.find_all("div", id="maincounter-wrap")
    global_deaths = None
    global_recovered = None
    for counter in main_counters:
        h1 = counter.find("h1")
        if not h1:
            continue
        heading = h1.get_text(strip=True)
        span = counter.find("span")
        if not span:
            continue
        value_text = span.get_text(strip=True)
        if "Deaths" in heading:
            global_deaths = value_text
        elif "Recovered" in heading:
            global_recovered = value_text

    if global_deaths is not None or global_recovered is not None:
        global_stats_str = f"{global_deaths}_{global_recovered}"
        global_hash = compute_content_hash(global_stats_str)
        cached_global_hash = get_cached_etag(global_key)
        if not (global_hash and cached_global_hash == global_hash):
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                if global_deaths is not None:
                    deaths_val = int(global_deaths.replace(",", ""))
                    cursor.execute("""
                        UPDATE state_metrics
                           SET metric_value = ?
                         WHERE state = 'United States' AND metric_type = 'COVID_Deaths'
                    """, (deaths_val,))
                    if cursor.rowcount == 0:
                        cursor.execute("""
                            INSERT INTO state_metrics
                                (state, metric_type, metric_value, year)
                            VALUES ('United States', 'COVID_Deaths', ?, 'Current')
                        """, (deaths_val,))
                if global_recovered is not None:
                    recovered_val = int(global_recovered.replace(",", ""))
                    cursor.execute("""
                        UPDATE state_metrics
                           SET metric_value = ?
                         WHERE state = 'United States' AND metric_type = 'COVID_Recovered'
                    """, (recovered_val,))
                    if cursor.rowcount == 0:
                        cursor.execute("""
                            INSERT INTO state_metrics
                                (state, metric_type, metric_value, year)
                            VALUES ('United States', 'COVID_Recovered', ?, 'Current')
                        """, (recovered_val,))
                conn.commit()
                conn.close()
                update_cached_etag(global_key, global_hash)
            except Exception as e:
                print("Error updating global stats in DB:", e)
    else:
        print("Failed to scrape global Deaths or Recovered numbers.")
    
    return state_processed



def download_rsv_data():
    csv_url = "https://data.cdc.gov/api/views/29hc-w46k/rows.csv?accessType=DOWNLOAD"
    local_filename = "rsv_data.csv"
    
    current_etag = None
    try:
        head_response = requests.head(csv_url)
        current_etag = head_response.headers.get('ETag')
        cached_etag = get_cached_etag(csv_url)
        if current_etag and cached_etag == current_etag:
            return None
        else:
            print("ETag changed or not available for RSV data. Proceeding with download.")
    except Exception as e:
        print("Error checking ETag for RSV data:", e)
    
    response = requests.get(csv_url)
    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        if current_etag:
            update_cached_etag(csv_url, current_etag)
        return local_filename
    else:
        print(f"Error downloading RSV data. Status code: {response.status_code}")
        return None

def parse_rsv_data(csv_filename):
    results = []
    with open(csv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            state = row.get("State", "")
            rate_str = row.get("Cumulative Rate", "0")
            year_str = row.get("Week ending date")
            try:
                rate_val = float(rate_str)
            except ValueError:
                print(f"Row {i}: Could not convert rate '{rate_str}' to float. Defaulting to 0.0")
                rate_val = 0.0
            results.append((state, rate_val, year_str))
    return results

def create_tables(db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            metric_type TEXT,   -- e.g., "COVID_Positivity", "RSV_Rate", "COVID_Cases"
            metric_value REAL,
            year TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state_centroids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT UNIQUE,
            latitude REAL,
            longitude REAL
        )
    """)
    
    conn.commit()
    conn.close()
    create_cache_table(db_name)

def insert_state_metrics(data, metric_type, db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for (state, metric_value, year) in data:
        cursor.execute("""
            INSERT INTO state_metrics (state, metric_type, metric_value, year)
            VALUES (?, ?, ?, ?)
        """, (state, metric_type, metric_value, year))
    
    conn.commit()
    conn.close()

def insert_state_centroids(centroid_dict, db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for state, (lat, lon) in centroid_dict.items():
        cursor.execute("""
            INSERT OR REPLACE INTO state_centroids (state, latitude, longitude)
            VALUES (?, ?, ?)
        """, (state, lat, lon))
    
    conn.commit()
    conn.close()

def cleanup():
    import os
    file_path = "./rsv_data.csv"
    try:
        os.unlink(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

def back_main():
    create_tables()
    
    covid_data = scrape_cdc_covid_data()
    if not covid_data:
        print("No new CDC COVID data to update (ETag unchanged).")
    else:
        insert_state_metrics(covid_data, metric_type="COVID_Positivity")
    
    updates = add_cases_to_db()
    if not updates:
        print("No new Worldometers COVID data to update.")
    else:
        print(f"Updated COVID_Cases for {len(updates)} locations.")

    rsv_csv = download_rsv_data()
    if rsv_csv is None:
        print("No new RSV data to update (ETag unchanged).")
    else:
        rsv_data = parse_rsv_data(rsv_csv)
        insert_state_metrics(rsv_data, metric_type="RSV_Rate")
    
    STATE_CENTROIDS = {
        "Alabama": (33.5207, -86.8025),        # Birmingham
        "Alaska": (61.2181, -149.9003),         # Anchorage
        "Arizona": (33.4484, -112.0740),        # Phoenix
        "Arkansas": (34.7465, -92.2896),        # Little Rock
        "California": (34.0522, -118.2437),     # Los Angeles
        "Colorado": (39.7392, -104.9903),       # Denver
        "Connecticut": (41.1865, -73.1950),     # Bridgeport
        "Delaware": (39.7447, -75.5484),        # Wilmington
        "District of Columbia": (38.9072, -77.0369),  # Washington, D.C.
        "Florida": (30.3322, -81.6557),         # Jacksonville
        "Georgia": (33.7490, -84.3880),         # Atlanta
        "Hawaii": (21.3069, -157.8583),         # Honolulu
        "Idaho": (43.6150, -116.2023),          # Boise
        "Illinois": (41.8781, -87.6298),        # Chicago
        "Indiana": (39.7684, -86.1581),         # Indianapolis
        "Iowa": (41.5868, -93.6250),            # Des Moines
        "Kansas": (37.6872, -97.3301),          # Wichita
        "Kentucky": (38.2527, -85.7585),        # Louisville
        "Louisiana": (29.9511, -90.0715),       # New Orleans
        "Maine": (43.6591, -70.2568),           # Portland, ME
        "Maryland": (39.2904, -76.6122),        # Baltimore
        "Massachusetts": (42.3601, -71.0589),   # Boston
        "Michigan": (42.3314, -83.0458),        # Detroit
        "Minnesota": (44.9778, -93.2650),       # Minneapolis
        "Mississippi": (32.2988, -90.1848),     # Jackson
        "Missouri": (39.0997, -94.5786),        # Kansas City, MO
        "Montana": (45.7833, -108.5007),        # Billings
        "Nebraska": (41.2565, -95.9345),        # Omaha
        "Nevada": (36.1699, -115.1398),         # Las Vegas
        "New Hampshire": (42.9956, -71.4548),   # Manchester
        "New Jersey": (40.7357, -74.1724),      # Newark
        "New Mexico": (35.0844, -106.6504),     # Albuquerque
        "New York": (40.7128, -74.0060),        # New York City
        "North Carolina": (35.2271, -80.8431),  # Charlotte
        "North Dakota": (46.8772, -96.7898),    # Fargo
        "Ohio": (39.9612, -82.9988),            # Columbus
        "Oklahoma": (35.4676, -97.5164),        # Oklahoma City
        "Oregon": (45.5051, -122.6750),         # Portland, OR
        "Pennsylvania": (39.9526, -75.1652),    # Philadelphia
        "Rhode Island": (41.8240, -71.4128),    # Providence
        "South Carolina": (32.7765, -79.9311),  # Charleston, SC
        "South Dakota": (43.5446, -96.7311),    # Sioux Falls
        "Tennessee": (36.1627, -86.7816),       # Nashville
        "Texas": (29.7604, -95.3698),           # Houston
        "Utah": (40.7608, -111.8910),           # Salt Lake City
        "Vermont": (44.4759, -73.2121),         # Burlington
        "Virginia": (36.8529, -75.9780),        # Virginia Beach
        "Washington": (47.6062, -122.3321),     # Seattle
        "West Virginia": (38.3498, -81.6326),   # Charleston, WV
        "Wisconsin": (43.0389, -87.9065),       # Milwaukee
        "Wyoming": (41.13998, -104.82025),      # Cheyenne
        "Puerto Rico": (18.4655, -66.1057)      # San Juan
    }
    
    insert_state_centroids(STATE_CENTROIDS)

    cleanup()

    start_gen()

# Uncomment the following lines to run the main process directly:
# if __name__ == "__main__":
#     back_main()