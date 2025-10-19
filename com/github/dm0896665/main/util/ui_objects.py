import re
import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QPalette, QResizeEvent

from PySide6.QtWidgets import QApplication, QGridLayout, QWidget, QMainWindow, QGraphicsPixmapItem


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Monster Pyter")
        self.setMinimumSize(700, 500)

    def closeEvent(self, event):
        sys.exit(0)


class CenteredWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        UiObjects.current_screen.ui.installEventFilter(self)
        self.widget_container_layout:QGridLayout = QGridLayout()
        self.center_container: QWidget = QWidget()
        self.center_container.setLayout(self.widget_container_layout)
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setObjectName("centered_widget")
        self.setStyleSheet('''
                            #centered_widget {
                                background-color: transparent;
                            }
                        ''')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.center_container.setParent(self)

        self.old_screen: QWidget = UiObjects.current_screen.ui
        self.old_screen.installEventFilter(self)

    def showEvent(self, event):
        self.setGeometry(self.old_screen.rect())

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(source.rect())
            self.old_screen.setGeometry(source.rect())
        return super().eventFilter(source, event)

    def resizeEvent(self, event):
        # Call the parent's resizeEvent first
        super().resizeEvent(event)

        # Calculate the new center location
        target_rect = UiObjects.window.centralWidget().geometry()
        x = target_rect.x() + (target_rect.width() - self.center_container.width()) / 2
        y = target_rect.y() + (target_rect.height() - self.center_container.height()) / 2

        # Move menu to center
        self.center_container.move(QPoint(int(x), int(y)))


class Screen(QWidget):
    def __init__(self, screen_name: str = None):
        super().__init__()
        self.background_image: str = None
        self.pixmap_unscaled: QGraphicsPixmapItem = None
        if screen_name is None:
            screen_name = self.camel_to_snake(self.__class__.__name__)
        self.screen_name = screen_name

        self.ui :QWidget = None

    def camel_to_snake(self, name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def on_screen_will_show(self):
        pass

    def on_screen_did_show(self):
        pass

    def on_screen_will_hide(self):
        pass

    def on_screen_did_hide(self):
        pass

    def set_up_background_image(self, pixmap: QGraphicsPixmapItem):
        if self.background_image is not None:
            self.pixmap_unscaled = pixmap
            pixmap = self.pixmap_unscaled.scaled(UiObjects.window.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
            p: QPalette = QPalette()
            p.setBrush(QPalette.Window, pixmap)
            self.parent().setPalette(p)
            self.setAutoFillBackground(True)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(source.rect())
            self.resize_function(source, event)
            if self.pixmap_unscaled is not None:
                self._resize_background()
        return super().eventFilter(source, event)

    def resize_function(self, source, event: QResizeEvent):
        pass

    def _resize_background(self):
        pixmap = self.pixmap_unscaled.scaled(UiObjects.window.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        p :QPalette = QPalette()
        p.setBrush(QPalette.Window, pixmap)
        self.parent().setPalette(p)

class UiObjects:
    app: QApplication = QApplication(sys.argv)
    window: GameWindow = GameWindow()
    current_screen: Screen = None
    old_screen: Screen = None
