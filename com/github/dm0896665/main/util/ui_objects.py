import re
import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QEvent, QPoint, Qt, QSignalBlocker, QObject, QPointF, QSize, QPropertyAnimation, QEventLoop, \
    QTimer
from PySide6.QtGui import QPalette, QResizeEvent, QPixmap, QColor, QPen, QFont, QTextCursor, QTextCharFormat, QBrush, \
    QRadialGradient, QPainter

from PySide6.QtWidgets import QApplication, QGridLayout, QWidget, QMainWindow, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView, QGraphicsSceneHoverEvent, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsOpacityEffect


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Monster Pyter")
        self.setMinimumSize(889, 500)

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
        if self.pixmap_unscaled:
            pixmap = self.pixmap_unscaled.scaled(UiObjects.window.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
            p: QPalette = QPalette()
            p.setBrush(QPalette.Window, pixmap)
            self.parent().setPalette(p)

    def toggle_visibility(self, graphics_item: QGraphicsItem | QWidget, duration: int=250):
        # Create an opacity effect and add it to the graphics item
        opacity_effect = QGraphicsOpacityEffect(opacity=1.0)
        graphics_item.setGraphicsEffect(opacity_effect)

        # Create a fade in animation
        fade_in_animation = QPropertyAnimation(
            propertyName=b"opacity",
            targetObject=opacity_effect,
            duration=duration,
            startValue=0.0,
            endValue=1.0,
        )

        # Create a loop that will run while the animation is running, and it the loop when it's done
        loop = QEventLoop()
        fade_in_animation.finished.connect(loop.quit)

        if graphics_item.isVisible():
            # Animation must be played backwards to fade out
            fade_in_animation.setDirection(QPropertyAnimation.Backward)
        else:
            # Show must be called for graphics item to be visible
            graphics_item.show()

        # Start fade animation
        fade_in_animation.start()
        loop.exec_()


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
        self.is_location = True

        # Setup object for hovering events
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # Configure pen to outline around location image on hover
        self.highlight_pen = QPen(QColor(UiObjects.highlight_color), 3, Qt.SolidLine)
        self.highlight_pen.setJoinStyle(Qt.RoundJoin)
        self.setShapeMode(QGraphicsPixmapItem.MaskShape)

        # Configure the text item for a transparent background and hide by default
        self.location_label = OutlinedGraphicsTextItem(name, self)
        self.location_label.setDefaultTextColor(QColor(UiObjects.dark_text_color))
        self.location_label.setVisible(False)

    def mousePressEvent(self, event):
        if self.callback:
            self.callback(self)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        # Update location label font size and outline size
        font_size = max(16, UiObjects.window.width() // 40)
        self.location_label.setFont(QFont(UiObjects.font_name, font_size))
        self.location_label.outlineFormat.setTextOutline(QPen(
            QColor(UiObjects.highlight_color), font_size / 5,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        ))

        # Update location of location label
        self.location_label.setPos(
            (self.pixmap().width() - self.location_label.boundingRect().width()) / 2,
            self.pixmap().height() if self.is_bottom_label else -(self.pixmap().height() / 4) - 7,
        )

        # update pen to outline around location image on hover
        self.highlight_pen = QPen(QColor(UiObjects.highlight_color), font_size / 6, Qt.SolidLine)

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
    def __init__(self, header_name: str = None, screen_name: str = None):
        super().__init__(screen_name)
        self.scene: QGraphicsScene = None
        self.view: QGraphicsView = None
        self.locations: list[MapLocation] = []

        # Header objects
        self.header_name: str = header_name
        self.header_label: QGraphicsTextItem = None
        self.header_box: QGraphicsRectItem = None

        # Customize Header visuals
        self.is_transparent_header: bool = True
        self.is_disappearing_header: bool = True

    def init_ui(self):
        # Initialize scene and view
        self.scene = QGraphicsScene(0, 0, self.ui.width(), self.ui.height())
        self.view = QGraphicsView(self.scene)

        # Hide background to show map behind view and remove padding to allow locations to be in top right corner
        self.view.setStyleSheet("background:rgba(0,0,0,0); padding: -36px;")

        # Add map header name
        if self.header_name:
            # Initialize header box/ container
            self.header_box = QGraphicsRectItem(0, 0, self.ui.width(), self.get_header_height())
            self.header_box.setPen(Qt.PenStyle.NoPen)
            self.set_radial_gradient_background()
            self.scene.addItem(self.header_box)

            # Initialize header label
            self.header_label = QGraphicsTextItem(self.header_name)
            self.header_label.setDefaultTextColor(QColor(UiObjects.dark_text_color))
            font_size = max(16, UiObjects.window.width() // 40)
            self.header_label.setFont(QFont(UiObjects.font_name, font_size))
            self.center_header_label()
            self.scene.addItem(self.header_label)

            # Hide header objects if header will be flashed
            if self.is_disappearing_header and self.is_transparent_header:
                self.header_box.hide()
                self.header_label.hide()

        # Add view to layout
        self.ui.layout().addWidget(self.view)

    def setup_locations(self):
        pass

    def set_radial_gradient_background(self):
        # Create a QRadialGradient object
        width: float = self.ui.width() / 2
        if self.is_transparent_header:
            width = self.ui.width() / 3
        gradient = QRadialGradient(
            # Center the gradient at the middle of the header_box's bounding rectangle
            QPointF(self.header_box.sceneBoundingRect().center()),
            # Set the radius to encompass the scene
            width
        )

        # Add color stops to the gradient
        # Stop 0.0 is the center color
        gradient.setColorAt(0.0, QColor(UiObjects.light_text_color))  # A lighter color

        # Stop 1.0 is the outer edge color
        outside_color = QColor("#1B1F3D")
        if self.is_transparent_header:
            outside_color.setAlpha(0)
        gradient.setColorAt(1.0, outside_color)  # A dark color

        # Create a QBrush with the radial gradient
        brush = QBrush(gradient)

        # Apply the brush to the QGraphicsScene
        self.header_box.setBrush(brush)

    def on_screen_will_hide(self):
        self.ui.layout().removeWidget(self.view)
        self.locations.clear()

    def add_location(self, map_location: MapLocation):
        # Relocate location based on if there is a header that moves the map down or not
        if self.header_name and not self.is_transparent_header and map_location.is_location:
            map_location.height_percent_location = map_location.height_percent_location + 5

        self.position_location_on_map(map_location)
        self.locations.append(map_location)

    def flash_map_header(self):
        if self.header_name and self.is_disappearing_header and self.is_transparent_header:
            self.toggle_visibility(self.header_box, 500)
            self.toggle_visibility(self.header_label, 500)
            QTimer.singleShot(2000,
                lambda: (
                    self.toggle_visibility(self.header_label, 750),
                    self.toggle_visibility(self.header_box, 750)
                )
            )

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
        # ---After new code changes, we shouldn't need fitInView, so some padding is still needed to be removed
        self.view.setStyleSheet("background:rgba(0,0,0,0); padding: -5px;")

        # Update scene size
        self.scene.setSceneRect(0, 0, self.ui.width(), self.ui.height())

        # Update header sizing
        if self.header_name:
            self.header_box.setRect(0, 0, self.ui.width(), int(self.get_header_height()))
            self.set_radial_gradient_background()
            font_size = max(16, UiObjects.window.width() // 40)
            self.header_label.setFont(QFont(UiObjects.font_name, font_size))
            self.center_header_label()

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

    def add_blank_area_to_pixmap(self, original_pixmap: QPixmap) -> QPixmap:
        """
        Adds a blank area to the top of a QPixmap.

        Args:
            original_pixmap: The original QPixmap to add padding to.

        Returns:
            A new QPixmap with the blank area at the top.
        """
        # Null check
        if original_pixmap.isNull():
            return QPixmap()

        # Get the dimensions of the original pixmap
        original_width = original_pixmap.width()
        original_height = original_pixmap.height()

        # Create a new pixmap with increased height
        new_size = QSize(original_width, original_height + self.get_header_height())
        new_pixmap = QPixmap(new_size)

        # Create a QPainter to draw on the new pixmap
        painter = QPainter(new_pixmap)

        # Draw the original pixmap onto the new one, offset by the top padding
        painter.drawPixmap(0, self.get_header_height(), original_pixmap)

        # End the painter
        painter.end()

        return new_pixmap

    def set_up_background_image(self, pixmap: QGraphicsPixmapItem):
        # Set high rez version of pixmap
        self.pixmap_unscaled = pixmap

        # Get the size of the map image
        size = UiObjects.window.size()
        if self.header_name and not self.is_transparent_header:
            size.setHeight(size.height() - self.get_header_height())

        # Scale the image to fit the screen
        pixmap = self.pixmap_unscaled.scaled(size, Qt.AspectRatioMode.IgnoreAspectRatio)

        # Add an extra blank area to move the map down if there is a non-transparent header
        if self.header_name and not self.is_transparent_header:
            pixmap = self.add_blank_area_to_pixmap(pixmap)

        # Set the pixmap to a palette
        p: QPalette = QPalette()
        p.setBrush(QPalette.Window, pixmap)

        # Add the image to the Screen
        self.parent().setPalette(p)
        self.setAutoFillBackground(True)

    def _resize_background(self):
        # If there is a background image, use the set up method as it will account for the screen size change
        if self.pixmap_unscaled:
            self.set_up_background_image(self.pixmap_unscaled)

    def get_header_height(self):
        return int(self.ui.height() * .15)

    def center_header_label(self):
        # Get the header rectangle
        header_box_rect = self.header_box.rect()

        # Get the text item's bounding rectangle in scene coordinates
        text_rect = self.header_label.boundingRect()

        # Calculate the center position in scene coordinates
        center_x = header_box_rect.width() / 2 - text_rect.width() / 2
        center_y = self.get_header_height() / 2 - text_rect.height() / 2

        # Set the position of the text item
        self.header_label.setPos(center_x, center_y)


class UiObjects:
    app: QApplication = QApplication(sys.argv)
    window: GameWindow = GameWindow()
    current_screen: Screen = None
    old_screen: Screen = None
    light_text_color: str = "#EAAB08"
    dark_text_color: str = "#6B3F02"
    highlight_color: str = "gold"
    font_name: str = "Harrington"
