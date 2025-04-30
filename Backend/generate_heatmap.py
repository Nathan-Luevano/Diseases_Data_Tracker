import sqlite3
import folium
from folium.plugins import HeatMap

def get_distinct_years(metric_type, db_name="health_data.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT SUBSTR(year, 1, 4)
            FROM state_metrics
            WHERE metric_type = ?
            ORDER BY SUBSTR(year, 1, 4)
        """
        cursor.execute(query, (metric_type,))
        rows = cursor.fetchall()
        years = [row[0] for row in rows if row[0]]
        return years
    except sqlite3.Error as e:
        print(f"Database error in get_distinct_years: {e}")
        return []
    finally:
        conn.close()

def fetch_heatmap_data(db_name="health_data.db", metric_type="COVID_Positivity", year_filter="Past 4 Weeks", exact_match=False):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if exact_match:
            query = """
                SELECT s.latitude, s.longitude, m.metric_value
                FROM state_centroids s
                JOIN state_metrics m ON s.state = m.state
                WHERE m.metric_type = ?
                  AND m.year = ?
                  AND s.latitude IS NOT NULL
                  AND s.longitude IS NOT NULL
            """
            cursor.execute(query, (metric_type, year_filter))
        else:
            query = """
                SELECT s.latitude, s.longitude, m.metric_value
                FROM state_centroids s
                JOIN state_metrics m ON s.state = m.state
                WHERE m.metric_type = ?
                  AND SUBSTR(m.year, 1, 4) = ?
                  AND s.latitude IS NOT NULL
                  AND s.longitude IS NOT NULL
            """
            cursor.execute(query, (metric_type, year_filter))

        rows = cursor.fetchall()
        
        data_for_heatmap = []
        for lat, lon, metric_value in rows:
            try:
                lat = float(lat)
                lon = float(lon)
                weight = float(metric_value)
                data_for_heatmap.append([lat, lon, weight])
            except (ValueError, TypeError):
                continue

        return data_for_heatmap

    except sqlite3.Error as e:
        print(f"Database error in fetch_heatmap_data: {e}")
        return []
    finally:
        conn.close()

def generate_heatmap_html(metric_type, year_filter, output_file="heatmap.html", exact_match=False):
    heatmap_data = fetch_heatmap_data(metric_type=metric_type, year_filter=year_filter, exact_match=exact_match)
    if not heatmap_data:
        print(f"No valid data found for '{metric_type}' with filter '{year_filter}'.")
        return

    try:
        m = folium.Map(location=[39.8283, -98.5795],
                       zoom_start=5,
                       tiles="cartodbpositron")

        HeatMap(
            data=heatmap_data,
            min_opacity=0.2,
            max_opacity=0.9,
            radius=25,
            blur=15,
            gradient={
                "0.2": "blue",
                "0.4": "lime",
               "0.6": "yellow",
                "0.8": "orange",
                "1.0": "red"
            }
        ).add_to(m)

        m.save(output_file)

    except Exception as e:
        print(f"Error generating heatmap for '{metric_type}', '{year_filter}': {e}")

def start_gen():
    disease_configs = {
        "COVID-19": {
            "metric_type": "COVID_Positivity",
            "years": ["Past 4 Weeks"],
            "exact_match": True
        },
        "RSV": {
            "metric_type": "RSV_Rate",
            "years": get_distinct_years("RSV_Rate"),  
            "exact_match": False
        }
    }

    for disease, config in disease_configs.items():
        metric_type = config["metric_type"]
        exact = config["exact_match"]
        
        for year_val in config["years"]:
            safe_disease = disease.replace(" ", "_")
            safe_year = year_val.replace(" ", "_")
            if safe_year == "Past_4_Weeks":
                safe_year = "Past-4-Weeks"
            output_file = f"heatmap_{safe_disease}_{safe_year}.html"

            generate_heatmap_html(metric_type, year_val, output_file, exact_match=exact)
