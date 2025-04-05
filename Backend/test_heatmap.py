import sqlite3
import requests
import folium
from folium.plugins import HeatMap

def get_state_metrics_summary(metric_type, db_name="health_data.db"):
    """
    Returns a dictionary mapping each state to the average metric value
    for the given metric_type.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = """
            SELECT state, AVG(metric_value)
            FROM state_metrics
            WHERE metric_type = ?
            GROUP BY state
        """
        cursor.execute(query, (metric_type,))
        rows = cursor.fetchall()
        print(f"DEBUG: get_state_metrics_summary fetched {len(rows)} rows.")
        return {row[0]: row[1] for row in rows}
    except Exception as e:
        print(f"Error in get_state_metrics_summary: {e}")
        return {}
    finally:
        conn.close()

def fetch_heatmap_data(db_name="health_data.db", metric_type="COVID_Positivity", year_filter="Past 4 Weeks", exact_match=False):
    """
    Returns a list of [latitude, longitude, weight] rows for the heatmap.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if exact_match:
            query = """
                SELECT s.latitude, s.longitude, m.metric_value
                FROM state_centroids s
                JOIN state_metrics m ON TRIM(s.state)=TRIM(m.state)
                WHERE m.metric_type = ?
                  AND m.year = ?
                  AND s.latitude IS NOT NULL
                  AND s.longitude IS NOT NULL
            """
            params = (metric_type, year_filter)
        else:
            query = """
                SELECT s.latitude, s.longitude, m.metric_value
                FROM state_centroids s
                JOIN state_metrics m ON TRIM(s.state)=TRIM(m.state)
                WHERE m.metric_type = ?
                  AND SUBSTR(m.year, 1, 4) = ?
                  AND s.latitude IS NOT NULL
                  AND s.longitude IS NOT NULL
            """
            params = (metric_type, year_filter)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print(f"DEBUG: fetch_heatmap_data fetched {len(rows)} rows for metric '{metric_type}' and year '{year_filter}'.")
        
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

        geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
        geojson_data = requests.get(geojson_url).json()

        state_metrics = get_state_metrics_summary(metric_type)
        print("DEBUG: State metrics summary (sample):", dict(list(state_metrics.items())[:5]))

        for feature in geojson_data["features"]:
            state_name = feature["properties"].get("name")
            if state_name in state_metrics:
                feature["properties"]["metric"] = round(state_metrics[state_name], 2)
            else:
                feature["properties"]["metric"] = "N/A"

        tooltip = folium.GeoJsonTooltip(
            fields=["name", "metric"],
            aliases=["State:", "Metric:"],
            localize=True
        )

        def style_function(feature):
            return {
                "fillOpacity": 0.1,
                "weight": 0,
                "color": "transparent",
            }

        folium.GeoJson(
            geojson_data,
            name="State Borders",
            style_function=style_function,
            tooltip=tooltip,
            highlight_function=lambda x: {"weight": 2, "color": "blue", "fillOpacity": 0.1}
        ).add_to(m)

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

        folium.LayerControl().add_to(m)
        m.save(output_file)
        print(f"Heatmap with state overlays generated: {output_file}")

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
        print(f"DEBUG: get_distinct_years for '{metric_type}' returned: {years}")
        return years
    except sqlite3.Error as e:
        print(f"Database error in get_distinct_years: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    generate_heatmap_html(metric_type="COVID_Positivity", year_filter="Past 4 Weeks", output_file="heatmap_with_overlays.html", exact_match=True)
