from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QRect, QAbstractAnimation
from PyQt6.QtGui import QIcon, QPainter
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy,
    QComboBox
)

# from pages.dashboard import create_dashboard_page
from pages.heatmap import create_heatmap_page
from pages.stats import create_stats_page
from pages.settings import create_settings_page

from widgets import ResizeHandle

class ModernDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self._is_maximized = False
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle("Health Dashboard")

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        self.title_bar = self.create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        nav_frame = self.create_left_nav()
        content_layout.addWidget(nav_frame)
        
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_frame)

        # self.dashboard_page = create_dashboard_page()
        
        self.heatmap_page, self.filter_sidebar_inpage = create_heatmap_page(
            self.toggle_inpage_sidebar
        )

        self.stats_page = create_stats_page()
        self.settings_page = create_settings_page()

        # self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.heatmap_page)
        self.stacked_widget.addWidget(self.stats_page)
        self.stacked_widget.addWidget(self.settings_page)

        self.overlay = self.create_overlay()
        self.overlay.setParent(self)
        self.overlay.raise_()
        self.overlay.hide()

        self.filter_sidebar = self.create_filter_sidebar()
        self.filter_sidebar.setParent(self)
        self.filter_sidebar.raise_()
        self.filter_sidebar.hide()

        self.resize_handle = ResizeHandle(self)
        self.resize_handle.show()

        self.sidebar_animation = None

    def create_title_bar(self):
        title_bar_frame = QFrame()
        title_bar_frame.setObjectName("TitleBar")
        title_bar_layout = QHBoxLayout(title_bar_frame)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)
        title_bar_layout.setSpacing(10)

        title_bar_frame.mousePressEvent = self.title_bar_mousePressEvent
        title_bar_frame.mouseMoveEvent = self.title_bar_mouseMoveEvent

        self.title_label = QLabel("Health Dashboard")
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        title_bar_layout.addWidget(self.title_label)

        title_bar_layout.addStretch()

        btn_minimize = QPushButton()
        btn_minimize.setIcon(QIcon("./icons/minus.svg"))
        btn_minimize.setObjectName("TitleBarButton")
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(btn_minimize)

        self.btn_maximize = QPushButton()
        self.btn_maximize.setIcon(QIcon("./icons/corners-out.svg"))
        self.btn_maximize.setObjectName("TitleBarButton")
        self.btn_maximize.setFixedSize(30, 30)
        self.btn_maximize.clicked.connect(self.toggle_max_restore)
        title_bar_layout.addWidget(self.btn_maximize)

        btn_close = QPushButton()
        btn_close.setIcon(QIcon("./icons/x.svg"))
        btn_close.setObjectName("TitleBarButton")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        title_bar_layout.addWidget(btn_close)

        return title_bar_frame

    def title_bar_mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.pos()
            event.accept()

    def title_bar_mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            new_pos = self.pos() + event.pos() - self._drag_pos
            self.move(new_pos)
            event.accept()

    def toggle_max_restore(self):
        if not self._is_maximized:
            self.showMaximized()
            self.resize_handle.hide()
            self._is_maximized = True
            self.btn_maximize.setIcon(QIcon("./icons/corners-in.svg"))
        else:
            self.showNormal()
            self._is_maximized = False
            self.resize_handle.show()
            self.btn_maximize.setIcon(QIcon("./icons/corners-out.svg"))

    def create_left_nav(self):
        nav_frame = QFrame()
        nav_frame.setObjectName("NavFrame")
        nav_frame.setFixedWidth(60)

        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(20)

        # btn_dashboard = QPushButton()
        # btn_dashboard.setIcon(QIcon("./icons/house.svg"))
        # btn_dashboard.setObjectName("NavButton")
        # btn_dashboard.setFixedSize(40, 40)
        # btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        # nav_layout.addWidget(btn_dashboard, 0, Qt.AlignmentFlag.AlignHCenter)

        btn_heatmap = QPushButton()
        btn_heatmap.setIcon(QIcon("./icons/gradient.svg"))
        btn_heatmap.setObjectName("NavButton")
        btn_heatmap.setFixedSize(40, 40)
        btn_heatmap.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        nav_layout.addWidget(btn_heatmap, 0, Qt.AlignmentFlag.AlignHCenter)

        btn_stats = QPushButton()
        btn_stats.setIcon(QIcon("./icons/chart-line.svg"))
        btn_stats.setObjectName("NavButton")
        btn_stats.setFixedSize(40, 40)
        btn_stats.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        nav_layout.addWidget(btn_stats, 0, Qt.AlignmentFlag.AlignHCenter)

        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon("./icons/faders-fill.svg"))
        btn_settings.setObjectName("NavButton")
        btn_settings.setFixedSize(40, 40)
        btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        nav_layout.addWidget(btn_settings, 0, Qt.AlignmentFlag.AlignHCenter)

        nav_layout.addStretch()
        return nav_frame

    def create_overlay(self):
        overlay = QFrame()
        overlay.setObjectName("Overlay")
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        overlay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        overlay.mousePressEvent = self.overlay_mouse_press
        return overlay

    def overlay_mouse_press(self, event):
        event.accept()
        self.toggle_filter_sidebar(force_close=True)

    def create_filter_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("FilterSidebar")
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)

        close_button = QPushButton("X")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(lambda: self.toggle_filter_sidebar(force_close=True))
        sidebar_layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)

        label = QLabel("Filter Options")
        label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        sidebar_layout.addWidget(label)

        disease_label = QLabel("Disease:")
        disease_label.setStyleSheet("color: #FFFFFF;")
        sidebar_layout.addWidget(disease_label)

        self.disease_combo = QComboBox()
        self.disease_combo.addItems(["COVID-19", "Flu", "RSV"])
        self.disease_combo.setStyleSheet("background-color: #2F3044; color: #FFFFFF;")
        sidebar_layout.addWidget(self.disease_combo)

        year_label = QLabel("Year:")
        year_label.setStyleSheet("color: #FFFFFF;")
        sidebar_layout.addWidget(year_label)

        self.year_combo = QComboBox()
        self.year_combo.addItems(["2020", "2021", "2022", "2023"])
        self.year_combo.setStyleSheet("background-color: #2F3044; color: #FFFFFF;")
        sidebar_layout.addWidget(self.year_combo)

        sidebar_layout.addStretch()
        return sidebar

    def toggle_filter_sidebar(self, force_close=False):
        sidebar_rect = self.filter_sidebar.geometry()
        start_x = sidebar_rect.x()
        end_x = start_x

        is_open = (start_x == self.width() - sidebar_rect.width())
        if is_open or force_close:
            end_x = self.width()
        else:
            self.overlay.setParent(self)
            self.filter_sidebar.setParent(self)
            self.filter_sidebar.show()
            self.overlay.show()
            self.overlay.raise_()
            self.filter_sidebar.raise_()
            end_x = self.width() - sidebar_rect.width()

        self.sidebar_anim = QPropertyAnimation(self.filter_sidebar, b"geometry")
        self.sidebar_anim.setDuration(300)
        self.sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        start_rect = QRect(start_x, sidebar_rect.y(), sidebar_rect.width(), sidebar_rect.height())
        end_rect = QRect(end_x, sidebar_rect.y(), sidebar_rect.width(), sidebar_rect.height())
        self.sidebar_anim.setStartValue(start_rect)
        self.sidebar_anim.setEndValue(end_rect)

        def on_finished():
            if end_x == self.width():
                self.filter_sidebar.hide()
                self.overlay.hide()

        self.sidebar_anim.finished.connect(on_finished)
        self.sidebar_anim.start()

    def toggle_inpage_sidebar(self):
        if hasattr(self, "sidebar_animation") and self.sidebar_animation is not None:
            if self.sidebar_animation.state() == QAbstractAnimation.State.Running:
                return

        current_width = self.filter_sidebar_inpage.maximumWidth()
        target_width = 300 if current_width == 0 else 0

        self.sidebar_animation = QPropertyAnimation(self.filter_sidebar_inpage, b"maximumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setStartValue(current_width)
        self.sidebar_animation.setEndValue(target_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.sidebar_animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        title_bar_height = self.title_bar.height()
        self.overlay.setGeometry(0, title_bar_height, self.width(), self.height() - title_bar_height)
        sidebar_width = self.filter_sidebar.width()
        current_x = self.filter_sidebar.x()
        new_x = self.width() - sidebar_width if self.filter_sidebar.isVisible() and current_x < self.width() else self.width()
        self.filter_sidebar.setGeometry(new_x, title_bar_height, sidebar_width, self.height() - title_bar_height)
        handle_size = self.resize_handle.size()
        self.resize_handle.move(self.width() - handle_size.width(), self.height() - handle_size.height())
