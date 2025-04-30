import os
import sys
import sqlite3
import pandas as pd
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QGroupBox,
                            QSizePolicy, QWidget, QMessageBox)
from PyQt6 import QtWebEngineWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'health_data.db')

STATE_POPULATIONS = {
    "Alabama": 5118425,
    "Alaska": 733583,
    "Arizona": 7359197,
    "Arkansas": 3045637,
    "California": 39029342,
    "Colorado": 5877610,
    "Connecticut": 3626205,
    "Delaware": 1018396,
    "Florida": 22484482,
    "Georgia": 11029227,
    "Hawaii": 1440196,
    "Idaho": 1965509,
    "Illinois": 12582032,
    "Indiana": 6833037,
    "Iowa": 3200517,
    "Kansas": 2942939,
    "Kentucky": 4512310,
    "Louisiana": 4590241,
    "Maine": 1385340,
    "Maryland": 6164660,
    "Massachusetts": 6981974,
    "Michigan": 10037261,
    "Minnesota": 5717184,
    "Mississippi": 2940057,
    "Missouri": 6177957,
    "Montana": 1122867,
    "Nebraska": 1967923,
    "Nevada": 3177772,
    "New Hampshire": 1395231,
    "New Jersey": 9261699,
    "New Mexico": 2113344,
    "New York": 19571216,
    "North Carolina": 10698973,
    "North Dakota": 779261,
    "Ohio": 11756058,
    "Oklahoma": 4019800,
    "Oregon": 4240137,
    "Pennsylvania": 12961683,
    "Rhode Island": 1093734,
    "South Carolina": 5342388,
    "South Dakota": 909824,
    "Tennessee": 7051339,
    "Texas": 30029572,
    "Utah": 3380800,
    "Vermont": 647064,
    "Virginia": 8683619,
    "Washington": 7785786,
    "West Virginia": 1775156,
    "Wisconsin": 5892539,
    "Wyoming": 581381,
    "District of Columbia": 671803
}


class HealthStatsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentFrame")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        try:
            self.conn = sqlite3.connect(DB_PATH)
            print(f"Connected to database at {DB_PATH}")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not connect to database: {e}")
            return
        
        self.load_filter_data()
        self.init_ui()
    
    def load_filter_data(self):
        """Load data needed for filters from the database"""
        try:
            self.metric_types = ['COVID_Cases', 'RSV_Rate']
            
            self.covid_years = ['Current']
            
            rsv_years_query = """
            SELECT DISTINCT substr(year, 1, 4) as year_value 
            FROM state_metrics 
            WHERE metric_type = 'RSV_Rate'
            ORDER BY year_value DESC
            """
            self.rsv_years = pd.read_sql(rsv_years_query, self.conn)['year_value'].tolist()
            
            self.rsv_years = [year for year in self.rsv_years if '2017' <= year <= '2023']
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading filter data: {e}")
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title_label = QLabel("Disease Statistics")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        filter_box = QGroupBox()
        filter_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        filter_box.setMaximumHeight(120)
        filter_box.setObjectName("FilterSidebar")
        filter_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QComboBox {
                background-color: #27293D;
                color: #FFFFFF;
                padding: 5px;
                border: 1px solid #444561;
                border-radius: 5px;
                min-height: 25px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #444561;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton {
                background-color: #2F3044;
                color: #FFFFFF;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444561;
            }
        """)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)
        
        metric_layout = QVBoxLayout()
        metric_label = QLabel("Disease Type:")
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(self.metric_types)
        self.metric_combo.currentTextChanged.connect(self.update_year_options)
        self.metric_combo.setMinimumWidth(150)
        metric_layout.addWidget(metric_label)
        metric_layout.addWidget(self.metric_combo)
        
        year_layout = QVBoxLayout()
        year_label = QLabel("Time Period:")
        self.year_combo = QComboBox()
        self.year_combo.addItems(self.covid_years)
        self.year_combo.setMinimumWidth(150)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        self.update_button = QPushButton("Update Visualization")
        self.update_button.setObjectName("TitleBarButton")
        self.update_button.clicked.connect(self.update_graphs)
        self.update_button.setMinimumWidth(150)
        button_layout.addWidget(self.update_button)
        
        filter_layout.addLayout(metric_layout)
        filter_layout.addLayout(year_layout)
        filter_layout.addStretch(1)  
        filter_layout.addLayout(button_layout)
        filter_box.setLayout(filter_layout)
        
        main_layout.addWidget(filter_box, 0)
        
        self.plot_container = QVBoxLayout()
        self.plot_container.setSpacing(15)
        
        plots_widget = QWidget()
        plots_widget.setLayout(self.plot_container)
        plots_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(plots_widget, 1)
        
        self.update_graphs()
    
    def update_year_options(self):
        """Update year options based on selected metric type"""
        self.year_combo.clear()
        
        selected_metric = self.metric_combo.currentText()
        if selected_metric == 'COVID_Cases':
            self.year_combo.addItems(self.covid_years)
        elif selected_metric == 'RSV_Rate':
            self.year_combo.addItems(self.rsv_years)
    
    def update_graphs(self):
        """Update graphs based on selected filters"""
        for i in reversed(range(self.plot_container.count())): 
            widget = self.plot_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        selected_metric = self.metric_combo.currentText()
        selected_year = self.year_combo.currentText()
        
        try:
            if selected_metric == 'COVID_Cases':
                self.display_covid_data()
            elif selected_metric == 'RSV_Rate':
                self.display_rsv_data(selected_year)
        except Exception as e:
            QMessageBox.warning(self, "Data Error", f"Error processing data: {e}")
    
    def display_covid_data(self):
        """Display COVID cases data"""
        try:
            query = "SELECT state, metric_value FROM state_metrics WHERE metric_type = 'COVID_Cases' AND year = 'Current'"
            data = pd.read_sql(query, self.conn)
            
            data = data[data['metric_value'] > 0]
            
            if data.empty:
                self.show_no_data_message()
                return
            
            data = data.sort_values('metric_value', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=data['state'], 
                    y=data['metric_value'],
                    marker_color='#1f77b4',  
                    hovertemplate='<b>%{x}</b><br>Cases: %{y:,.0f}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title={
                    'text': 'COVID-19 Cases by State',
                    'font': {'color': 'white', 'size': 20}
                },
                xaxis_title={'text': 'State', 'font': {'color': 'white', 'size': 14}},
                yaxis_title={'text': 'Number of Cases', 'font': {'color': 'white', 'size': 14}},
                xaxis={'tickfont': {'color': 'white'}},
                yaxis={'tickfont': {'color': 'white'}},
                plot_bgcolor='#27293D',  
                paper_bgcolor='#27293D',
                margin=dict(l=40, r=40, t=60, b=40),
            )
            
            plot_widget = self.create_plot_widget(fig, "COVID-19 Cases")
            self.plot_container.addWidget(plot_widget)
            
        except Exception as e:
            QMessageBox.warning(self, "Data Error", f"Error processing COVID data: {e}")
    
    def display_rsv_data(self, year):
        """Display RSV rate data for the specified year"""
        try:
            query = f"""
            SELECT t1.state, t1.metric_value, t1.year
            FROM state_metrics t1
            JOIN (
                SELECT state, MIN(year) as min_year
                FROM state_metrics
                WHERE metric_type = 'RSV_Rate' AND year LIKE '{year}%'
                GROUP BY state
            ) t2 ON t1.state = t2.state AND t1.year = t2.min_year
            WHERE t1.metric_type = 'RSV_Rate'
            """
            
            rsv_data = pd.read_sql(query, self.conn)
            
            if rsv_data.empty:
                self.show_no_data_message()
                return
            
            def calculate_rsv_cases(row):
                state_name = row['state']
                rate = row['metric_value']
                
                if state_name in STATE_POPULATIONS:
                    population = STATE_POPULATIONS[state_name]
                    return (rate / 100) * population / 1000
                return 0
            
            rsv_data['calculated_cases'] = rsv_data.apply(calculate_rsv_cases, axis=1)
            
            rsv_data = rsv_data[rsv_data['calculated_cases'] > 0]
            
            if rsv_data.empty:
                self.show_no_data_message()
                return
            
            rsv_data = rsv_data.sort_values('calculated_cases', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=rsv_data['state'], 
                    y=rsv_data['calculated_cases'],
                    marker_color='#ff7f0e',  
                    hovertemplate='<b>%{x}</b><br>Cases (thousands): %{y:,.1f}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title={
                    'text': f'Estimated RSV Cases by State (in thousands) ({year})',
                    'font': {'color': 'white', 'size': 20}
                },
                xaxis_title={'text': 'State', 'font': {'color': 'white', 'size': 14}},
                yaxis_title={'text': 'Estimated Cases (thousands)', 'font': {'color': 'white', 'size': 14}},
                xaxis={'tickfont': {'color': 'white'}},
                yaxis={'tickfont': {'color': 'white'}},
                plot_bgcolor='#27293D',
                paper_bgcolor='#27293D',
                margin=dict(l=40, r=40, t=60, b=40),
                height=600
            )
            
            plot_widget = self.create_plot_widget(fig, f"RSV Cases ({year})")
            self.plot_container.addWidget(plot_widget)
            
        except Exception as e:
            QMessageBox.warning(self, "Data Error", f"Error processing RSV data: {e}")
    
    def show_no_data_message(self):
        """Show message when no data is available"""
        no_data_label = QLabel("No data available for the selected filters.")
        no_data_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plot_container.addWidget(no_data_label)
    
    def create_plot_widget(self, fig, title):
        """Create a widget containing a Plotly plot"""
        plot_box = QGroupBox(title)
        plot_box.setObjectName("FilterSidebar")  
        plot_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                border-radius: 10px;
                padding-top: 15px;
            }
        """)
        
        plot_layout = QVBoxLayout()
        
        plot_html = plot(fig, output_type='div', include_plotlyjs='cdn')
        
        web_view = QWebEngineView()
        web_view.setHtml(plot_html)
        web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        plot_layout.addWidget(web_view)
        plot_box.setLayout(plot_layout)
        
        return plot_box

    def cleanup(self):
        """Close database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            print("Database connection closed")


def create_stats_page():
    """Create and return the stats page widget"""
    widget = HealthStatsWidget()
    return widget