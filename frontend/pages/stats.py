from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

def create_stats_page():
    page = QFrame()
    layout = QVBoxLayout(page)
    label = QLabel("Statistics Page Content Here")
    label.setStyleSheet("color: #FFFFFF; font-size: 18px;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    return page
