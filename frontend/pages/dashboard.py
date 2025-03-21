from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

def create_dashboard_page():
    page = QFrame()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header_layout = QHBoxLayout()
    header_layout.addStretch()
    layout.addLayout(header_layout)

    placeholder_label = QLabel("Dashboard Page Content Here")
    placeholder_label.setStyleSheet("color: #FFFFFF; font-size: 18px;")
    placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(placeholder_label)

    return page
