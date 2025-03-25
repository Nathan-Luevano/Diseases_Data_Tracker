from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter
from PyQt6.QtWidgets import QFrame

class ResizeHandle(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.icon = QIcon("./frontend/icons/notches.svg")
        self.setStyleSheet("background-color: transparent; border-radius: 10px")
        self._drag_active = False
        self._drag_start_pos = None
        self._start_window_size = None

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.icon.pixmap(self.size())
        painter.drawPixmap(self.rect(), pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_start_pos = event.globalPosition() if hasattr(event, 'globalPosition') else event.globalPos()
            self._start_window_size = self.parent().size()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            current_pos = event.globalPosition() if hasattr(event, 'globalPosition') else event.globalPos()
            delta = current_pos - self._drag_start_pos
            new_width = max(self._start_window_size.width() + int(delta.x()), 400)
            new_height = max(self._start_window_size.height() + int(delta.y()), 300)
            self.parent().resize(new_width, new_height)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()
