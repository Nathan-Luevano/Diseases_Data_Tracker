from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sqlite3
import math

class RoundedImageLabel(QLabel):
    def __init__(self, corner_radius=20, parent=None):
        super().__init__(parent)
        self._corner_radius = corner_radius

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPainterPath
        from PyQt6.QtCore import QRectF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, self._corner_radius, self._corner_radius)
        painter.setClipPath(path)
        super().paintEvent(event)


def create_stat_card(icon_path: str, number_text: str, label_text: str) -> QFrame:
    card_frame = QFrame()
    card_frame.setStyleSheet("background-color: #2F3044; border-radius: 20px;")

    card_layout = QVBoxLayout(card_frame)
    card_layout.setContentsMargins(10, 10, 10, 10)
    card_layout.setSpacing(5)

    icon_label = QLabel()
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pixmap = QPixmap(icon_path)
    if not pixmap.isNull():
        scaled_icon = pixmap.scaled(
            64, 64,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(scaled_icon)
    else:
        icon_label.setText("(No Icon)")
        icon_label.setStyleSheet("color: #FFFFFF;")
    card_layout.addWidget(icon_label)

    number_label = QLabel(number_text)
    number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    number_label.setStyleSheet("color: #FFFFFF; font-size: 24px;")
    card_layout.addWidget(number_label)

    descriptor_label = QLabel(label_text)
    descriptor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    descriptor_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
    card_layout.addWidget(descriptor_label)

    return card_frame

def get_metric_average(metric_type: str, db_name="health_data.db") -> float:
    """Return the average metric_value for the given metric_type."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT AVG(metric_value) FROM state_metrics WHERE metric_type = ?",
        (metric_type,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result if result is not None else 0.0

def create_dashboard_page(go_to_heatmap, go_to_stats):
    page = QFrame()
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    additional_frame = QFrame()
    additional_frame.setFixedHeight(200)
    additional_frame.setStyleSheet("background-color: transparent;")

    stat_layout = QHBoxLayout(additional_frame)
    stat_layout.setSpacing(20)
    stat_layout.setContentsMargins(0, 0, 0, 0)

    positivity = get_metric_average("COVID_Positivity")
    active_cases = (positivity / 100) * 340000000


    recovered = get_metric_average("COVID_Recovered")
    deaths = get_metric_average("COVID_Deaths")

    active_cases_formatted = f"{math.ceil(active_cases):,}"
    deaths_formatted = f"{math.ceil(deaths):,}"
    recovered_formatted = f"{math.ceil(recovered):,}"
    
    stat_layout.addWidget(create_stat_card("./frontend/icons/virus-bold.svg", active_cases_formatted, "Active Cases"))
    stat_layout.addWidget(create_stat_card("./frontend/icons/face-mask-bold.svg", recovered_formatted, "Recovered"))
    stat_layout.addWidget(create_stat_card("./frontend/icons/skull-bold.svg", deaths_formatted, "Deaths"))

    main_layout.addWidget(additional_frame)

    content_layout = QHBoxLayout()
    content_layout.setSpacing(20)

    map_button = QPushButton()
    map_button.setFixedSize(600, 400)
    map_button.setStyleSheet("""
        QPushButton {
            background-color: #2F3044;
            border-radius: 20px;
        }
        QPushButton:hover {
            background-color: #44455A;
        }
    """)
    map_button.clicked.connect(go_to_heatmap)

    map_layout = QVBoxLayout(map_button)
    map_layout.setContentsMargins(0, 0, 0, 0)
    map_layout.setSpacing(0)

    map_label = RoundedImageLabel(20)
    map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pixmap = QPixmap("./frontend/pages/samp_heatmap.png")
    if not pixmap.isNull():
        scaled_pixmap = pixmap.scaled(
            600, 400,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        map_label.setPixmap(scaled_pixmap)
    else:
        map_label.setText("Map Preview Placeholder")
        map_label.setStyleSheet("color: #FFFFFF;")  

    map_layout.addWidget(map_label)
    content_layout.addWidget(map_button)

    data_button = QPushButton()
    data_button.setFixedSize(300, 400)
    data_button.setStyleSheet("""
        QPushButton {
            background-color: #2F3044;
            border-radius: 20px;
        }
        QPushButton:hover {
            background-color: #44455A;
        }
    """)
    data_button.clicked.connect(go_to_stats)

    data_layout = QVBoxLayout(data_button)
    data_layout.setContentsMargins(0, 0, 0, 0)
    data_layout.setSpacing(0)

    data_label = QLabel("Data Widgets Placeholder")
    data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    data_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
    data_layout.addWidget(data_label)

    content_layout.addWidget(data_button)

    main_layout.addLayout(content_layout)

    return page
