from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

def create_heatmap_page(toggle_inpage_sidebar_callback):
    """
    pass in any callback or data the page needs. 
    For example, a function reference for toggling sidebars.
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
    filter_button.setIcon(QIcon("./icons/funnel-fill.svg"))
    filter_button.setStyleSheet("color: #FFFFFF; font-size: 16px;")
    filter_button.clicked.connect(toggle_inpage_sidebar_callback)
    header_layout.addWidget(filter_button)
    content_layout.addLayout(header_layout)
    
    label = QLabel("Heatmap Page Content Here")
    label.setStyleSheet("color: #FFFFFF; font-size: 18px;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    content_layout.addWidget(label)
    
    sidebar = QFrame()
    sidebar.setObjectName("InpageSidebar")
    sidebar.setStyleSheet("""
        #InpageSidebar {
            background-color: #232430;  
            border-top-left-radius: 15px;
            border-bottom-left-radius: 15px;
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
    label_filter.setStyleSheet("color: #FFFFFF; font-size: 16px;")
    sidebar_layout.addWidget(label_filter)
    
    disease_label = QLabel("Disease:")
    disease_label.setStyleSheet("color: #FFFFFF;")
    sidebar_layout.addWidget(disease_label)
    
    disease_combo = QComboBox()
    disease_combo.addItems(["COVID-19", "Flu", "RSV"])
    disease_combo.setStyleSheet("""
        QComboBox {
            background-color: #2F3044;
            color: #FFFFFF;
            border: 1px solid #1d1e2b;
            border-radius: 5px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border: none;
        }
    """)
    sidebar_layout.addWidget(disease_combo)
    
    year_label = QLabel("Year:")
    year_label.setStyleSheet("color: #FFFFFF;")
    sidebar_layout.addWidget(year_label)
    
    year_combo = QComboBox()
    year_combo.addItems(["2020", "2021", "2022", "2023"])
    year_combo.setStyleSheet("""
        QComboBox {
            background-color: #2F3044;
            color: #FFFFFF;
            border: 1px solid #1d1e2b;
            border-radius: 5px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border: none;
        }
    """)
    sidebar_layout.addWidget(year_combo)
    sidebar_layout.addStretch()
    
    sidebar.setMaximumWidth(0)
    
    layout.addWidget(content_widget)
    layout.addWidget(sidebar)
    layout.setStretch(0, 1)
    layout.setStretch(1, 0)
    
    return page, sidebar
