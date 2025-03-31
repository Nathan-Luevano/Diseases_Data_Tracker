from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from pathlib import Path

def create_heatmap_page(toggle_inpage_sidebar_callback):
    """
    Create the heatmap page with an embedded QWebEngineView to display the heatmap HTML file.
    The displayed file is updated automatically based on filter selections.
    """
    page = QFrame()
    layout = QHBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(10, 10, 10, 10)
    content_layout.setSpacing(10)
    
    header_layout = QHBoxLayout()
    header_layout.addStretch()
    
    filter_button = QPushButton()
    filter_button.setIcon(QIcon("./frontend/icons/funnel-fill.svg"))
    filter_button.setStyleSheet("color: #FFFFFF; font-size: 16px; border-radius: 10px")
    filter_button.clicked.connect(toggle_inpage_sidebar_callback)
    header_layout.addWidget(filter_button)
    content_layout.addLayout(header_layout)
    
    heatmap_display = QWebEngineView()
    heatmap_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    default_disease = "COVID-19"
    default_year = "Past-4-Weeks"  
    safe_disease = default_disease.replace(" ", "_")
    safe_year = default_year.replace(" ", "")
    base_dir = Path(__file__).resolve().parent.parent.parent
    default_filepath = base_dir / f"heatmap_{safe_disease}_{safe_year}.html"
    heatmap_display.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    heatmap_display.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    heatmap_display.setUrl(QUrl.fromLocalFile(str(default_filepath)))
    content_layout.addWidget(heatmap_display)
    
    sidebar = QFrame()
    sidebar.setObjectName("InpageSidebar")
    sidebar.setStyleSheet("""
        #InpageSidebar {
            background-color: #232430;  
            border-top-left-radius: 15px;
            border-bottom-left-radius: 15px;
            border-radius: 10px
        }
    """)
    sidebar_layout = QVBoxLayout(sidebar)
    sidebar_layout.setContentsMargins(20, 20, 20, 20)
    sidebar_layout.setSpacing(20)
    
    close_button = QPushButton("X")
    close_button.setFixedSize(30, 30)
    close_button.clicked.connect(toggle_inpage_sidebar_callback)
    sidebar_layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
    
    label_filter = QLabel("Filter Options")
    label_filter.setStyleSheet("color: #FFFFFF; font-size: 16px; border-radius: 10px")
    sidebar_layout.addWidget(label_filter)
    
    disease_label = QLabel("Disease:")
    disease_label.setStyleSheet("color: #FFFFFF; border-radius: 10px")
    sidebar_layout.addWidget(disease_label)
    
    disease_combo = QComboBox()
    disease_combo.addItems(["COVID-19", "RSV"])
    disease_combo.setStyleSheet("""
        QComboBox {
            background-color: #2F3044;
            color: #FFFFFF;
            border: 1px solid #1d1e2b;
            border-radius: 10px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border: none;
            border-radius: 10px;
        }
    """)
    sidebar_layout.addWidget(disease_combo)
    
    year_label = QLabel("Year:")
    year_label.setStyleSheet("color: #FFFFFF;")
    sidebar_layout.addWidget(year_label)
    
    year_combo = QComboBox()
    year_combo.addItems(["Past-4-Weeks","2023", "2022", "2021", "2020","2019","2018","2017" ])
    year_combo.setStyleSheet("""
        QComboBox {
            background-color: #2F3044;
            color: #FFFFFF;
            border: 1px solid #1d1e2b;
            border-radius: 10px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border: none;
            border-radius: 10px;
        }
    """)
    sidebar_layout.addWidget(year_combo)
    sidebar_layout.addStretch()
    
    sidebar.setMaximumWidth(0)
    
    layout.addWidget(content_widget)
    layout.addWidget(sidebar)
    layout.setStretch(0, 1)
    layout.setStretch(1, 0)
    
    def update_heatmap():
        selected_disease = disease_combo.currentText()
        if selected_disease == "COVID-19":
            year_combo.blockSignals(True)
            year_combo.clear()
            year_combo.addItems(["Past-4-Weeks"])
            year_combo.blockSignals(False)
        elif selected_disease == "RSV":
            year_combo.blockSignals(True)
            year_combo.clear()
            year_combo.addItems(["2023", "2022", "2021", "2020", "2019", "2018", "2017"])
            year_combo.blockSignals(False)
        selected_year = year_combo.currentText()
        safe_disease = selected_disease.replace(" ", "_")
        safe_year = selected_year.replace(" ", "")
        base_dir = Path(__file__).resolve().parent.parent.parent
        filepath = base_dir / f"heatmap_{safe_disease}_{safe_year}.html"
        heatmap_display.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        heatmap_display.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        file_url = QUrl.fromLocalFile(str(filepath))
        heatmap_display.setUrl(file_url)
    
    disease_combo.currentIndexChanged.connect(update_heatmap)
    year_combo.currentIndexChanged.connect(update_heatmap)
    
    return page, sidebar
