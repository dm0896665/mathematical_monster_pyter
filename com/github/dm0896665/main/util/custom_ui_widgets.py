from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class CustomGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent;")
        self.setFrameStyle(QtWidgets.QGraphicsView.NoFrame)

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), aspectRadioMode=Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)