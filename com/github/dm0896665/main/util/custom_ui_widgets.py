from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

from com.github.dm0896665.main.util.ui_objects import UiObjects


class CustomGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent;")
        self.setFrameStyle(QtWidgets.QGraphicsView.NoFrame)

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), aspectRadioMode=Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

class Button(QtWidgets.QPushButton):
    def __init__(self, text:str = None, parent=None):
        super().__init__(text, parent)
        darker_light_color = QColor(UiObjects.light_text_color).darker(120).name()
        self.setStyleSheet("""
                    QPushButton {
                        background-color: """ + UiObjects.light_text_color + """;
                        color: """ + UiObjects.dark_text_color + """;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        font-size: 20px;
                        border: 2px solid """ + UiObjects.dark_text_color + """;
                    }
                    QPushButton:hover {
                        color: """ + UiObjects.highlight_color + """;
                        border: 2px solid """ + UiObjects.highlight_color + """;
                    }
                    QPushButton:pressed {
                        background-color: """ + darker_light_color + """;
                        color: """ + UiObjects.highlight_color + """;
                        border: 2px solid """ + UiObjects.highlight_color + """;
                    }
                """)

    def resizeEvent(self, event):
        super().resizeEvent(event)