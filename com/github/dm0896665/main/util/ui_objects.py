import re
import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QEvent, QPoint, Qt, QSignalBlocker, QObject
from PySide6.QtGui import QPalette, QResizeEvent, QPixmap, QColor, QPen, QFont, QTextCursor, QTextCharFormat

from PySide6.QtWidgets import QApplication, QGridLayout, QWidget, QMainWindow, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView, QGraphicsSceneHoverEvent, QGraphicsTextItem


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
        self.widget_container_layout: QGridLayout = QGridLayout()
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
        self.pixmap_unscaled: QGraphicsPixmapItem = None
        if screen_name is None:
            screen_name = self.camel_to_snake(self.__class__.__name__)
        self.screen_name = screen_name
        self.screen_image_location = "screens/" + screen_name + "/"
        self.previous_screen: Screen = None

        self.ui: QWidget = None

    def get_screen_image_path(self, image_name) -> str:
        return self.screen_image_location + image_name

    def camel_to_snake(self, name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def init_ui(self):
        pass

    def on_screen_will_show(self):
        pass

    def on_screen_did_show(self):
        pass

    def on_screen_will_hide(self):
        pass

    def on_screen_did_hide(self):
        pass

    def set_up_background_image(self, pixmap: QGraphicsPixmapItem):
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
        p: QPalette = QPalette()
        p.setBrush(QPalette.Window, pixmap)
        self.parent().setPalette(p)


class OutlinedGraphicsTextItem(QGraphicsTextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.outlineFormat = QTextCharFormat()
        self.outlineFormat.setTextOutline(QPen(
            Qt.GlobalColor.yellow, 4,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        ))
        self.dummyFormat = QTextCharFormat()
        self.dummyFormat.setTextOutline(QPen(Qt.GlobalColor.transparent))

        children = self.findChildren(QObject)
        if not children:
            super().setPlainText('')
            children = self.findChildren(QObject)
        if self.toPlainText():
            # ensure we call our version of setPlainText()
            self.setPlainText(self.toPlainText())

        for obj in children:
            if obj.metaObject().className() == 'QWidgetTextControl':
                self.textControl = obj
                break

    def setPlainText(self, text):
        super().setPlainText(text)
        if text:
            format = QTextCharFormat()
            cursor = QTextCursor(self.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.mergeCharFormat(format)

    def paint(self, painter, option, widget):
        with QSignalBlocker(self.textControl):
            cursor = QTextCursor(self.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.mergeCharFormat(self.outlineFormat)
            super().paint(painter, option, widget)
            cursor.mergeCharFormat(self.dummyFormat)
            super().paint(painter, option, widget)


class MapLocation(QGraphicsPixmapItem):
    def __init__(self, pix_map: QPixmap, name: str, width_percent: int, height_percent: int,
                 width_percent_location: int, height_percent_location: int, callback=None, is_bottom_label: bool = False):
        super().__init__(pix_map)
        self.name = name
        self.callback = callback
        self.width_percent = width_percent
        self.height_percent = height_percent
        self.width_percent_location = width_percent_location
        self.height_percent_location = height_percent_location
        self.original_pixmap = pix_map
        self.is_bottom_label = is_bottom_label

        # Setup object for hovering events
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # Configure pen to outline around location image on hover
        self.highlight_pen = QPen(QColor("gold"), 3, Qt.SolidLine)
        self.highlight_pen.setJoinStyle(Qt.RoundJoin)
        self.setShapeMode(QGraphicsPixmapItem.MaskShape)

        # Configure the text item for a transparent background and hide by default
        self.location_label = OutlinedGraphicsTextItem(name, self)
        self.location_label.setDefaultTextColor(QColor("black"))
        self.location_label.setVisible(False)

    def mousePressEvent(self, event):
        if self.callback:
            self.callback(self)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        # Update location label font size and outline size
        font_size = max(16, UiObjects.window.width() // 40)
        self.location_label.setFont(QFont("Arial", font_size))
        self.location_label.outlineFormat.setTextOutline(QPen(
            Qt.GlobalColor.yellow, font_size / 5,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        ))

        # Update location of location label
        self.location_label.setPos(
            (self.pixmap().width() - self.location_label.boundingRect().width()) / 2,
            self.pixmap().height() if self.is_bottom_label else -(self.pixmap().height() / 4) - 7,
        )

        # Show location label and location outline
        self.location_label.setVisible(True)
        self._is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        # Hide location label and remove location outline
        self.location_label.setVisible(False)
        self._is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        # If user is hovering over location, outline the location
        if self._is_hovered:
            outline_path = self.shape()
            painter.setPen(self.highlight_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(outline_path)


class MapScreen(Screen):
    def __init__(self, screen_name: str = None):
        super().__init__(screen_name)
        self.scene: QGraphicsScene = None
        self.view: QGraphicsView = None
        self.locations: list[MapLocation] = []

    def init_ui(self):
        # Initialize scene and view
        self.scene = QGraphicsScene(0, 0, self.ui.width(), self.ui.height())
        self.view = QGraphicsView(self.scene)

        # Hide background to show map behind view and remove padding to allow locations to be in top right corner
        self.view.setStyleSheet("background:rgba(0,0,0,0); padding: -36px; ")

        # Add view to layout
        self.ui.layout().addWidget(self.view)

    def on_screen_will_hide(self):
        self.ui.layout().removeWidget(self.view)
        self.locations.clear()

    def add_location(self, map_location: MapLocation):
        self.position_location_on_map(map_location)
        self.locations.append(map_location)

    def eventFilter(self, source, event):
        # Overriding eventFilter, so all previous resize functions also need to be called
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(source.rect())
            self.resize_function(source, event)
            self.reposition_locations()
            if self.pixmap_unscaled is not None:
                self._resize_background()
        return super().eventFilter(source, event)

    def reposition_locations(self):
        # Remove padding changes because view.fitInView changes the padding
        # (but fitInView doesn't change the padding initially for some reason)
        self.view.setStyleSheet("background:rgba(0,0,0,0);")

        # Update scene/ view size
        self.scene.setSceneRect(0, 0, self.ui.width(), self.ui.height())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        # Update location position
        for location in self.locations:
            self.scene.removeItem(location)
            self.position_location_on_map(location)

    def position_location_on_map(self, location: MapLocation):
        # Get current screen size
        width: int = self.ui.width()
        height: int = self.ui.height()

        # Calculate new width and height
        desired_width: int = location.width_percent / 100 * width
        desired_height: int = location.height_percent / 100 * height

        # Scale location image based on screen size
        pixmap: QPixmap = location.original_pixmap.scaled(desired_width, desired_height)
        location.setPixmap(pixmap)

        # Position location on map
        x = location.width_percent_location / 100 * width
        y = location.height_percent_location / 100 * height
        location.setPos(x, y)

        # Add location to scene/ view
        self.scene.addItem(location)

    def get_map_location_image_path(self, image_name) -> str:
        return "screens/map_locations/" + image_name


class UiObjects:
    app: QApplication = QApplication(sys.argv)
    window: GameWindow = GameWindow()
    current_screen: Screen = None
    old_screen: Screen = None
