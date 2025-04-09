from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

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

def create_dashboard_page(go_to_heatmap, go_to_stats):
    page = QFrame()
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    additional_button = QPushButton()
    additional_button.setFixedHeight(200)
    additional_button.setStyleSheet("""
        QPushButton {
            background-color: #2F3044;
            border-radius: 20px;
        }
        QPushButton:hover {
            background-color: #44455A;
        }
    """)
    additional_button.clicked.connect(go_to_stats)  

    additional_layout = QVBoxLayout(additional_button)
    additional_layout.setContentsMargins(0, 0, 0, 0)
    additional_layout.setSpacing(0)

    additional_label = QLabel("Additional Data Placeholder")
    additional_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    additional_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
    additional_layout.addWidget(additional_label)

    main_layout.addWidget(additional_button)

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
