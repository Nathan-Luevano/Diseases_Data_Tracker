# Diseases Data Tracker

**Empowering Public Health Through Data**

## Mission

Diseases Data Tracker is dedicated to aggregating and visualizing the latest data on disease testing. Our mission is to empower public health professionals, researchers, and the community with clear, actionable insights to better understand trends across various illnesses. This application offers a comprehensive way to track positive test data and monitor health metrics in real time.

---

## What We Offer

- **Real-Time Data Scraping:** Automated retrieval of data from trusted sources like the CDC and Worldometers.
- **Interactive Visualizations:** Dynamic dashboards and heatmaps that make data exploration intuitive.
- **Historical Trends & Analysis:** Statistical analysis and visual insights into disease trends over time.
- **Customizable Reports:** Easy-to-use interfaces to generate detailed reports on regional and national scales.
- **Modular Architecture:** Backend data processing and a feature-rich frontend built on PyQt for seamless user interaction.

---

## Screenshots

<!-- Add your application screenshots below -->
![Dashboard Screenshot](/frontend/pages/dash_samp.png)
![Heatmap Screenshot](/frontend/pages/heatmap_samp.png)
<!-- Add more images as needed -->

---

## How It Works

1. **Backend Data Processing:**
   - **Scraping Data:** The `scrape_cdc_covid_data()` function in [Backend/main.py](Backend/main.py) retrieves the latest COVID-19 data using Selenium or Requests-HTML when appropriate.
   - **Database Management:** Functions like `create_tables()`, `insert_state_metrics()`, and `insert_state_centroids()` manage and update the SQLite database with current information.
   - **Data Cleanup:** Temporary files (e.g., RSV data) are automatically removed after processing via the `cleanup()` function.

2. **Frontend Visualization:**
   - **Modern Dashboard:** The [ModernDashboard](frontend/dash.py) class provides an interactive GUI for accessing various data views.
   - **Dynamic Pages:** Different pages (e.g., dashboard, stats, and heatmap) are implemented across the [frontend/pages](frontend/pages) directory to visualize data through charts, tables, and maps.
   - **Interactive Navigation:** Buttons and menus allow users to switch between detailed statistics and geographical heatmaps seamlessly.

3. **Integration & Execution:**
   - The main application is initiated via the [main.py](main.py) file, which calls `back_main()` to update data before launching the PyQt application.
   - The process is optimized for quick start-up times while ensuring data is always as current as possible.

---

## Dependencies

Ensure you have Python and pip installed. Then, install the required packages using:

```bash
pip install requests requests-html pyqt6 folium PyQt6-WebEngine lxml_html_clean matplotlib plotly pandas selenium
```

### Linux Specific Requirements

- Ensure you have `libxcb-cursor0`.
- Ensure your version of `gcc` is `12.1.0`.

---

## Running the Application

Simply run the main file with the current file structure:

```bash
python main.py
```

---

## Project Structure

- **Backend:** Contains scripts for data scraping, database operations, and data processing ([Backend/main.py](Backend/main.py)).
- **Frontend:** Houses the PyQt application components such as the dashboard and data visualization pages ([frontend/main.py](frontend/main.py) and [frontend/dash.py](frontend/dash.py)).
- **Database:** The application uses an SQLite database (`health_data.db`) to store and update health data.
- **Styles:** Custom stylesheets are stored (e.g., `styles.qss`) to maintain a consistent look and feel of the GUI.

---

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT License](LICENSE)

---