import sqlite3
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QComboBox
import datetime


def query_data(metric, year, db_name="health_data.db"):
    """
    Queries the database for average metric_value by state filtering on the given metric type and year.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    query = """
        SELECT state, AVG(metric_value) as avg_value 
        FROM state_metrics 
        WHERE metric_type = ? AND year = ?
        GROUP BY state
        ORDER BY state
    """
    cursor.execute(query, (metric, year))
    results = cursor.fetchall()
    conn.close()
    return results

def create_stats_page():
    page = QFrame()
    main_layout = QVBoxLayout(page)
        
    filter_layout = QHBoxLayout()
    disease_combo = QComboBox()
    disease_combo.addItems(["COVID-19", "RSV"])
    filter_layout.addWidget(disease_combo)
    
    time_combo = QComboBox()
    time_combo.addItems(["Past-4-Weeks", "Current"])
    filter_layout.addWidget(time_combo)
    
    main_layout.addLayout(filter_layout)
    
    try:
        from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg as FigureCanvas
    except ImportError:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    canvas = FigureCanvas(fig)
    main_layout.addWidget(canvas)
    
    def update_time_options():
        """
        Update the time options when the disease selection changes.
        """
        selected_disease = disease_combo.currentText()
        time_combo.blockSignals(True)
        time_combo.clear()
        if selected_disease == "COVID-19":
            time_combo.addItems(["Past-4-Weeks", "Current"])
        elif selected_disease == "RSV":
            time_combo.addItems([str(year) for year in range(2017, 2026)])
        time_combo.blockSignals(False)
        update_chart()
    
    def update_chart():
        selected_disease = disease_combo.currentText()
        selected_time    = time_combo.currentText()

        metric = "COVID_Cases" if selected_disease=="COVID-19" else "RSV_Rate"

        ax.clear()
        ax.set_facecolor("#2F3044")
        fig.patch.set_facecolor("#2F3044")

        ax.tick_params(colors="white", which="both")
        for spine in ax.spines.values():
            spine.set_color("white")

        if metric == "COVID_Cases":
            if selected_time == "Current":
                year_param = datetime.date.today().year
            elif selected_time == "Past-4-Weeks":
                year_param = None
            else:
                year_param = int(selected_time)
        else:
            year_param = int(selected_time)

        data = query_data(metric, year_param) if year_param else []
        if not data:
            ax.text(
                0.5, 0.5, "No data available",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=16, color="white"
            )
        else:
            states, values = zip(*data)
            ax.bar(states, values)
            ax.set_title(f"{selected_disease} – {selected_time}", color="white")
            ax.set_xlabel("State", color="white")
            ax.set_ylabel("Average Metric Value", color="white")
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        canvas.draw()
    
    disease_combo.currentIndexChanged.connect(update_time_options)
    time_combo.currentIndexChanged.connect(update_chart)
    
    update_time_options()
    
    return page