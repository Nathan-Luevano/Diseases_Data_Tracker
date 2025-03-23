import sys
import csv
import sqlite3
import requests
from requests_html import HTMLSession

def scrape_cdc_covid_data():
    url = "https://covid.cdc.gov/covid-data-tracker/#maps_positivity-4-week"
    
    session = HTMLSession()
    r = session.get(url)
    
    r.html.render(sleep=3)
    
    table = r.html.find("table", first=True)
    if not table:
        print("No table found.")
        return []
    
    rows = table.find("tr")
    data = []
    
    for row in rows:
        cells = row.find("td, th")
        data.append([cell.text for cell in cells])
    return data

def parse_covid_data(table_data):
    if not table_data:
        return []
    
    header = table_data[0]
    try:
        state_index = header.index("State/Territory")
    except ValueError:
        state_index = 0
    try:
        positivity_index = header.index("Test positivity (%) in past week")
    except ValueError:
        positivity_index = 2
    
    results = []
    for row in table_data[1:]:
        if len(row) > max(state_index, positivity_index):
            state = row[state_index]
            positivity_str = row[positivity_index]
            try:
                positivity_val = float(positivity_str)
            except ValueError:
                positivity_val = 0.0
            results.append((state, positivity_val, "Past 4 Weeks"))
    return results

def download_rsv_data():
    csv_url = "https://data.cdc.gov/api/views/29hc-w46k/rows.csv?accessType=DOWNLOAD"
    local_filename = "rsv_data.csv"
    response = requests.get(csv_url)
    with open(local_filename, "wb") as f:
        f.write(response.content)
    return local_filename

def parse_rsv_data(csv_filename):
    results = []
    with open(csv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = row.get("State", "")
            rate_str = row.get("Cumulative Rate", "0")
            year_str = row.get("Week ending date")
            try:
                rate_val = float(rate_str)
            except ValueError:
                rate_val = 0.0
            try:
                year_val = year_str
            except ValueError:
                pass
            results.append((state, rate_val, year_val))
    return results

def create_tables(db_name="health_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            metric_type TEXT,   -- e.g., "COVID_Positivity" or "RSV_Rate"
            metric_value REAL,
            year INTEGER
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


def main():
    create_tables()
    
    table_data = scrape_cdc_covid_data()
    covid_data = parse_covid_data(table_data)
    
    insert_state_metrics(covid_data, metric_type="COVID_Positivity")
    
    rsv_csv = download_rsv_data()
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

    print("All data inserted into the database successfully.")

if __name__ == "__main__":
    sys.exit(main())
