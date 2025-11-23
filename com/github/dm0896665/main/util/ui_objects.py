import math
import re
import sys
from enum import Enum
from typing import Callable, Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QEvent, QPoint, Qt, QSignalBlocker, QObject, QPointF, QSize, QPropertyAnimation, QEventLoop, \
    QTimer, Signal, QEasingCurve
from PySide6.QtGui import QPalette, QResizeEvent, QPixmap, QColor, QPen, QFont, QTextCursor, QTextCharFormat, QBrush, \
    QRadialGradient, QPainter, QCursor, QFontMetrics, QPainterPath, QIcon, QMouseEvent, QWheelEvent, QEnterEvent

from PySide6.QtWidgets import QApplication, QGridLayout, QWidget, QMainWindow, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView, QGraphicsSceneHoverEvent, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsOpacityEffect, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QFrame

from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.core.weapon.weapon import Weapon
from com.github.dm0896665.main.util.image_util import ImageUtil


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

class CenteredFocusWidget(QtWidgets.QWidget):
    def __init__(self, center_widget: QWidget, center_widget_width_percent: int = None, center_widget_height_percent: int = None, parent: QWidget = None):
        super().__init__(parent)
        # Set center widget proportions
        self.center_widget_width_percent = center_widget_width_percent
        self.center_widget_height_percent = center_widget_height_percent

        # Set center widget
        self.center_widget: QWidget = center_widget
        self.resize_center_widget()

        # Create a container to maintain horizontal center
        self.centered_widget_container_h = QWidget()
        self.centered_widget_container_h.setLayout(QHBoxLayout())
        self.centered_widget_container_h.layout().addWidget(self.center_widget)
        self.centered_widget_container_h.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centered_widget_container_h.setStyleSheet("background-color: transparent;")

        # Create a container to maintain vertical center
        self.centered_widget_container_v = QWidget()
        self.centered_widget_container_v.setLayout(QVBoxLayout())
        self.centered_widget_container_v.layout().addWidget(self.centered_widget_container_h)
        self.centered_widget_container_v.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centered_widget_container_v.setStyleSheet("background-color: transparent;")

        # Set main width and height to cover screen
        self.setFixedWidth(UiObjects.current_screen.ui.width())
        self.setFixedHeight(UiObjects.current_screen.ui.height())

        # Add centered widget to the main container
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.centered_widget_container_v)

        # Set background color to be semi-transparent
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet("QWidget {background-color: rgba(64,64,64,.64);}")

        # Capture events for resizing later
        UiObjects.current_screen.ui.installEventFilter(self)

    def eventFilter(self, source: QWidget, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.setFixedWidth(UiObjects.current_screen.ui.width())
            self.setFixedHeight(UiObjects.current_screen.ui.height())

            self.resize_center_widget()
        return super().eventFilter(source, event)

    def resize_center_widget(self):
        # If there are no set proportions, just make sure the centered widget is taking up all it should
        if self.center_widget_width_percent is None or self.center_widget_height_percent is None:
            self.center_widget.adjustSize()
        else:
            # Otherwise, set the proportions relative to the main window
            self.center_widget.setMaximumWidth(UiObjects.current_screen.ui.width() * (self.center_widget_width_percent/100))
            self.center_widget.setMaximumHeight(UiObjects.current_screen.ui.height() * (self.center_widget_height_percent/100))


class TransparentGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent;")
        self.setFrameStyle(QtWidgets.QGraphicsView.NoFrame)
        self.viewport().setMouseTracking(True)
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), aspectRadioMode=Qt.AspectRatioMode.KeepAspectRatio)

# Helper class for HighlightOnHoverGraphicsItem
class HighlightOnHoverGraphicsItemSignals(QObject):
    paint_finished = Signal()

class HighlightOnHoverGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, image_path: str, is_bottom_label: bool = True):
        self.connection = HighlightOnHoverGraphicsItemSignals()
        self.original_pixmap: QPixmap = ImageUtil.load_image_map(image_path)
        super().__init__(self.original_pixmap)
        self.is_bottom_label = is_bottom_label

        # Setup object for hovering events
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # Configure pen to outline around location image on hover
        self.highlight_pen = QPen(QColor(UiObjects.highlight_color), 3, Qt.SolidLine)
        self.highlight_pen.setJoinStyle(Qt.RoundJoin)
        self.setShapeMode(QGraphicsPixmapItem.MaskShape)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        # update pen to outline around location image on hover
        self.highlight_pen = QPen(
            QColor(UiObjects.highlight_color), max(16, UiObjects.window.width() // 40) / 6,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )

        # Show image outline
        self._is_hovered = True
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        # Remove image outline
        self._is_hovered = False
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
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
            self.connection.paint_finished.emit()

class BackButton(QtWidgets.QWidget):
    def __init__(self, parent: QWidget, on_click: Callable[[], None], width_percentage: int = 7, height_percentage: int = 10):
        super().__init__(parent)
        # Set width and height
        self.width_percentage: int = width_percentage
        self.height_percentage: int = height_percentage

        # Load 'back' image
        self.original_pixmap: QPixmap = ImageUtil.load_image_map("map_locations/back.png")
        self.back_image: QGraphicsPixmapItem = QGraphicsPixmapItem(self.original_pixmap)

        # Allow 'back' image to be highlighted on hover
        self.back_image_highlighted: QPixmap = self.original_pixmap

        # Set pen/painter to highlight back button image
        highlight_pen = QPen(
                QColor(UiObjects.highlight_color), max(16, UiObjects.window.width() // 40/2),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
        highlight_pen.setJoinStyle(Qt.RoundJoin)
        painter = QPainter(self.back_image_highlighted)
        painter.setPen(highlight_pen)
        painter.setBrush(Qt.NoBrush)
        outline_path = self.back_image.shape()
        painter.drawPath(outline_path)
        painter.end()

        # Set up back button with image
        self.button = QtWidgets.QPushButton()
        self.button.setIcon(QIcon(self.back_image.pixmap()))
        self.button.setIconSize(self.get_size())

        # Detect mouse for highlighting on hover and on click
        self.button.setMouseTracking(True)
        self.button.installEventFilter(self)
        self.button.clicked.connect(on_click)
        UiObjects.window.installEventFilter(self)

        # Set up on hover label and default it to be hidden
        self.hover_label = OutlinedLabel("Back", 30, UiObjects.highlight_color)
        self.hover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_policy = self.hover_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True) # Don't adjust layout when hidden
        self.hover_label.setSizePolicy(size_policy)
        self.hover_label.hide()

        # Setup layout with button and hover label below it
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.button)
        layout.addWidget(self.hover_label)

        # Setup styles and move to top-left of the screen with a little space from the corner
        self.adjustSize()
        self.setStyleSheet("background-color: transparent;"
                            "border: 1px solid transparent;")
        self.move(5, 5)

    def eventFilter(self, source: QWidget, event: QEvent):
        # Make sure button is sized properly when the screen resizes
        if event.type() == QEvent.Type.Resize:
            self.button.setIconSize(self.get_size())
            self.button.adjustSize()
            self.adjustSize()

        # Show highlighted image and label when hovering over button; otherwise, show regular image and hide the label
        if source == self.button:
            if event.type() == QEvent.Type.Enter:
                self.set_button_icon(self.back_image_highlighted)
                self.hover_label.show()
            elif event.type() == QEvent.Type.Leave:
                self.set_button_icon(self.back_image.pixmap())
                self.button.adjustSize()
                self.hover_label.hide()
        return super().eventFilter(source, event)

    def set_button_icon(self, back_image: QPixmap):
        self.button.setIcon(back_image)
        self.button.setIconSize(self.get_size())
        self.adjustSize()
        
    def get_size(self) -> QSize:
        return QSize(self.get_width(), self.get_height())

    def get_width(self) -> int:
        return int(self.width_percentage/100*UiObjects.window.width())

    def get_height(self) -> int:
        return int(self.height_percentage/100*UiObjects.window.height())


class Button(QtWidgets.QPushButton):
    def __init__(self, text:str = None, font_size: int = 20, parent=None):
        super().__init__(text, parent)

        # Set up button styles
        darker_light_color = QColor(UiObjects.light_text_color).darker(120).name()
        self.setStyleSheet("""
                    QPushButton {
                        background-color: """ + UiObjects.light_text_color + """;
                        color: """ + UiObjects.dark_text_color + """;
                        padding: 10px 10px;
                        border: none;
                        border-radius: 5px;
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
                    QPushButton:disabled {
                        background-color: """ + QColor(UiObjects.light_text_color).darker(130).name() + """;
                        color: """ + QColor(UiObjects.dark_text_color).darker(120).name() + """;
                        border: 2px solid """ + QColor(UiObjects.dark_text_color).darker(120).name() + """;
                    }
                """)
        self.window_size_divisor = max(1, int(154 * pow(.99, font_size * 3)))
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))

class Label(QtWidgets.QLabel):
    def __init__(self, text:str = None, font_size: int = 20, parent=None):
        super().__init__(parent)
        self.setText(text)
        # This converts the font size to a window width divisor with the divisor decreasing as font_size increases
        self.window_size_divisor = max(1, int(154 * pow(.99, font_size * 3)))
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))
        self.setStyleSheet("color: " + UiObjects.dark_text_color + "; background-color: transparent;")
        self.setWordWrap(True)

        UiObjects.current_screen.ui.installEventFilter(self)

    def resize_label(self):
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))

    def eventFilter(self, source: QWidget, event: QEvent):
        # Make sure widget is sized properly when the screen resizes
        if event.type() == QEvent.Type.Resize:
            self.resize_label()
        return super().eventFilter(source, event)


class OutlinedLabel(Label):

    def __init__(self, text:str = None, font_size: int = 20, outline_color=None, parent=None):
        super().__init__(text, font_size, parent)
        self.brush: QBrush = None
        self.pen: QPen = None
        self.w = 1 / 8
        self.mode = True
        self.set_brush(UiObjects.dark_text_color)
        if not outline_color:
            outline_color = UiObjects.light_text_color
        self.set_pen(outline_color)

    def scaled_outline_mode(self):
        return self.mode

    def set_scaled_outline_mode(self, state):
        self.mode = state

    def outline_thickness(self):
        return self.w * self.font().pointSize() if self.mode else self.w

    def set_outline_thickness(self, value):
        self.w = value

    def set_brush(self, brush):
        if not isinstance(brush, QBrush):
            brush = QBrush(brush)
        self.brush = brush

    def set_pen(self, pen):
        if not isinstance(pen, QPen):
            pen = QPen(pen)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen

    def sizeHint(self):
        w = math.ceil(self.outline_thickness() * 2)
        return super().sizeHint() + QSize(w, w)

    def minimumSizeHint(self):
        w = math.ceil(self.outline_thickness() * 2)
        return super().minimumSizeHint() + QSize(w, w)

    def paintEvent(self, event):
        w = self.outline_thickness()
        rect = self.rect()
        metrics = QFontMetrics(self.font())
        tr = metrics.boundingRect(self.text()).adjusted(0, 0, w, w)
        if self.indent() == -1:
            if self.frameWidth():
                indent = (metrics.boundingRect('x').width() + w * 2) / 2
            else:
                indent = w
        else:
            indent = self.indent()

        if self.alignment() & Qt.AlignLeft:
            x = rect.left() + indent - min(metrics.leftBearing(self.text()[0]), 0)
        elif self.alignment() & Qt.AlignRight:
            x = rect.x() + rect.width() - indent - tr.width()
        else:
            x = (rect.width() - tr.width()) / 2

        if self.alignment() & Qt.AlignTop:
            y = rect.top() + indent + metrics.ascent()
        elif self.alignment() & Qt.AlignBottom:
            y = rect.y() + rect.height() - indent - metrics.descent()
        else:
            y = (rect.height() + metrics.ascent() - metrics.descent()) / 2

        path = QPainterPath()
        path.addText(x, y, self.font(), self.text())
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)

        self.pen.setWidthF(w * 2)
        qp.strokePath(path, self.pen)
        qp.fillPath(path, self.brush)


class IntegerInput(QtWidgets.QLineEdit):
    def __init__(self, parent=None, text:str = None):
        super().__init__(parent)
        font_size = max(16, UiObjects.window.width() // 60)
        self.setFont(QFont(UiObjects.font_name, font_size))
        self.setStyleSheet("color: " + UiObjects.dark_text_color + "; background-color: " + UiObjects.light_text_color + ";" + "border: 2px solid " + UiObjects.dark_text_color + ";")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        font_size = max(16, UiObjects.window.width() // 60)
        self.setFont(QFont(UiObjects.font_name, font_size))

class PlayerStatusWidget(QtWidgets.QWidget):
    def __init__(self, player: Player, parent: QWidget):
        super().__init__(parent)
        # Set up layout
        self.setLayout(QVBoxLayout())

        # Set up player variables
        self.player = player
        self.player.property_change_listener.connect(self.player_property_change)

        # Set up expanding and collapsing animation
        self.size_animation: QPropertyAnimation = QPropertyAnimation(self, b"size")
        self.size_animation.setDuration(200)
        self.size_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.final_size_animation: QPropertyAnimation = QPropertyAnimation(self, b"size")
        self.final_size_animation.setDuration(self.size_animation.duration())
        self.final_size_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.move_animation: QPropertyAnimation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(self.size_animation.duration())
        self.move_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_expanding: bool = False
        self.is_collapsing: bool = False
        self.expanded_size: QSize = self.size() # Will determine later
        self.collapsed_size: QSize = self.size()

        # Set up top (regular size) widget
        self.player_container = QWidget()
        self.player_container.setLayout(QHBoxLayout())
        self.player_container.setMouseTracking(True)

        # Set up name label
        self.name_label: Label = Label(self.player.name, 16)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.player_container.layout().addWidget(self.name_label)

        # Set up name/level separator
        self.name_separator = QFrame()
        self.name_separator.setFrameShape(QFrame.VLine)  # Set the frame shape to VLine
        self.name_separator.setFrameShadow(QFrame.Sunken)  # Add a 3D effect
        self.name_separator.setLineWidth(1)
        self.player_container.layout().addWidget(self.name_separator)

        # Set up level label
        self.level_label: Label = Label("Level: " + str(self.player.level), 10)
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.player_container.layout().addWidget(self.level_label)

        # Add top (regular size) widget to layout
        self.layout().addWidget(self.player_container)

        # Set up (expanded size bott) widget
        self.status_container = QWidget()
        self.status_container.setLayout(QHBoxLayout())

        # Set up weapon section
        self.weapon_status_container = QVBoxLayout()
        self.weapon_image: TransparentGraphicsView = TransparentGraphicsView()
        self.weapon_status_container.addWidget(self.weapon_image)
        self.weapon_name_label: Label = Label("", 10)
        self.weapon_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weapon_status_container.addWidget(self.weapon_name_label)
        self.update_selected_weapon(self.player.selected_weapon)

        # Set up separator for expanded section
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)  # Set the frame shape to VLine
        self.separator.setFrameShadow(QFrame.Sunken)  # Add a 3D effect
        self.separator.setLineWidth(2)

        # Set up main info section
        self.stats_status_container = QVBoxLayout()
        self.health_label: Label = Label("", 16)
        self.health_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.update_health(self.player.health)
        self.stats_status_container.addWidget(self.health_label)
        self.strength_label: Label = Label("", 16)
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.update_strength(self.player.strength)
        self.stats_status_container.addWidget(self.strength_label)
        self.coins_label: Label = Label("", 16)
        self.coins_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.update_money(self.player.money)
        self.stats_status_container.addWidget(self.coins_label)

        # Add label, separator, and weapon section to (expanded size) bottom widget then add that to layout
        self.status_container.layout().addLayout(self.stats_status_container)
        self.status_container.layout().addWidget(self.separator)
        self.status_container.layout().addLayout(self.weapon_status_container)
        self.layout().addWidget(self.status_container)

        # Initialize (expanded size) bottom widget as hidden
        self.status_container.hide()

        # Enable mouse events
        self.setMouseTracking(True)

        # Set up main widget styles
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("border: 2px solid " + UiObjects.dark_text_color + ";"
                                            "border-radius: 13%;"
                                            "background-color: " + UiObjects.get_transparent_light_background_color(200) + ";")

        # Set up info styles
        item_styles: str = "border: 2px solid transparent; background-color: transparent;"
        self.name_label.setStyleSheet(item_styles)
        self.name_separator.setStyleSheet("background-color: " + UiObjects.dark_text_color + ";")
        self.level_label.setStyleSheet(item_styles)
        self.weapon_image.setStyleSheet(item_styles)
        self.weapon_name_label.setStyleSheet(item_styles)
        self.separator.setStyleSheet("background-color: " + UiObjects.dark_text_color + ";")
        self.health_label.setStyleSheet(item_styles + " color: red;")
        self.strength_label.setStyleSheet(item_styles + " color: blue;")
        self.coins_label.setStyleSheet(item_styles + " color: " + UiObjects.dark_text_color + ";")

        # Set up main container styles
        self.player_container.setStyleSheet(item_styles)
        self.status_container.setStyleSheet(item_styles)

        # Enable event filter
        UiObjects.current_screen.ui.installEventFilter(self)

        # Make sure widget is sized properly
        self.resize_widget()


    def player_property_change(self, name: str, value: Any):
        match name:
            case Player.name.fget.__name__:
                self.update_name(value)
            case Player.level.fget.__name__:
                self.update_level(value)
            case Player.selected_weapon.fget.__name__:
                self.update_selected_weapon(value)
            case Player.health.fget.__name__:
                self.update_health(value)
            case Player.strength.fget.__name__:
                self.update_strength(value)
            case Player.money.fget.__name__:
                self.update_money(value)

    def update_name(self, value: str):
        self.name_label.setText(value)
        self.resize_widget()

    def update_level(self, value: int):
        self.level_label.setText("Level: " + str(value))
        self.resize_widget()

    def update_selected_weapon(self, weapon: Weapon):
        self.weapon_image.setScene(
            ImageUtil.load_image("weapons/" + weapon.weapon_image_name + ".png"))
        self.weapon_name_label.setText(str(weapon.weapon_name))
        self.resize_widget()

    def update_health(self, value: int):
        self.health_label.setText(str(value) + "hp")
        self.resize_widget()

    def update_strength(self, value: int):
        self.strength_label.setText(str(value) + " strength")
        self.resize_widget()

    def update_money(self, value: int):
        self.coins_label.setText(str(value) + " coins")
        self.resize_widget()

    def eventFilter(self, source: QWidget, event: QEvent):
        # Make sure widget is sized properly when the screen resizes
        if event.type() == QEvent.Type.Resize:
            self.resize_widget()
        return super().eventFilter(source, event)

    def resize_widget(self):
        # If we are expanding/collapsing the widget, cancel it and make sure it's collapsed
        if self.is_collapsing or self.is_expanding:
            self.collapse_widget()
            self.is_collapsing = False
            self.is_expanding = False

        # Resize weapon image
        self.update_weapon_image_size()
        self.adjustSize()

        # After labels are resized, make sure the widget is sized and positioned properly then update size variables
        QTimer.singleShot(2, self.update_size_variables)

    def update_size_variables(self):
        self.adjustSize()
        # If the widget is expanded set variables properly and revert to regular size
        # as this method shouldn't be called when it's expanded, but it does happen from time to time
        if self.status_container.isVisible():
            # Get expanded Size
            self.expanded_size = self.size()

            # Collapse widget and get the collapsed size
            self.collapse_widget()
            self.collapsed_size = self.size()
        else:
            # If the widget is collapsed, set variables properly
            self.collapsed_size = self.size()

            # Get expanded widget size
            self.expand_widget()
            self.expanded_size = self.size()

            # Collapse widget and make sure it's positioned properly
            self.collapse_widget()
            self.move(self.get_position_for_size(self.collapsed_size))

        # Expanded width should never be smaller than the regular width
        if self.expanded_size.width() < self.collapsed_size.width():
            self.expanded_size.setWidth(self.collapsed_size.width())

    def collapse_widget(self):
        self.status_container.hide()
        self.name_separator.show()
        self.adjustSize()

    def expand_widget(self):
        self.status_container.show()
        self.name_separator.hide()
        self.adjustSize()

    @staticmethod
    def get_position_for_size(size: QSize):
        return QPoint(UiObjects.current_screen.ui.width() - size.width() - 5, 5)

    def update_weapon_image_size(self):
        height = UiObjects.current_screen.ui.height()
        self.weapon_image.setMaximumHeight(height / 10)

    def enterEvent(self, event: QEnterEvent):
        # Ignore if the widget is expanding/ retracting
        if self.is_expanding or self.is_collapsing:
            super().leaveEvent(event)
            return

        # Set to enlarging and hide the name separator
        self.is_expanding = True
        self.name_separator.hide()

        # Enlarge widget
        QTimer.singleShot(1, lambda: self.expand_collapse_widget())

        super().enterEvent(event)

    def leaveEvent(self, event: QEnterEvent):
        # Ignore if the widget is expanding/ retracting
        if self.is_collapsing or self.is_expanding:
            super().leaveEvent(event)
            return

        # Set to collapsing
        self.is_collapsing = True

        # Minimize widget
        QTimer.singleShot(1, lambda: self.expand_collapse_widget())

        super().leaveEvent(event)

    def expand_collapse_widget(self):
        self.adjustSize()

        # Set up variables based on sizing method
        initial_size = self.expanded_size if self.is_collapsing else self.collapsed_size
        new_size = self.collapsed_size if self.is_collapsing else self.expanded_size
        initial_pos = self.pos()

        # Get transition size (expanded size width and regular size height)
        temp_size: QSize = QSize(self.expanded_size.width(), self.collapsed_size.height())

        # If transition size is already met
        if self.is_expanding and temp_size.width() == self.collapsed_size.width():
            self.finish_status_widget_size_adjustment(temp_size, new_size, None)
            return

        # Set up size animation
        self.size_animation.setStartValue(initial_size)
        self.size_animation.setEndValue(temp_size)
        self.size_animation.finished.connect(lambda: self.finish_status_widget_size_adjustment(temp_size, new_size, initial_pos if self.is_collapsing else None))

        if self.is_collapsing:
            # When collapsing, hide the bottom widget part way through
            QTimer.singleShot(self.size_animation.duration() * .2, self.status_container.hide)
        else:
            # When expanding, set up move animation to happen at the same time to give the illusion of expanding to the left
            self.move_animation.setStartValue(initial_pos)
            self.move_animation.setEndValue(self.get_position_for_size(new_size))
            self.move_animation.start()

        # Start size adjustment animation
        self.size_animation.start()

    def finish_status_widget_size_adjustment(self, temp_size, new_size, initial_pos: QPoint = None):
        # Reset handler on size animation
        self.size_animation.finished.disconnect()

        # If expand/collapse was canceled, return
        if not self.is_collapsing and not self.is_expanding:
            return

        # Set up final size animation
        self.final_size_animation.setStartValue(temp_size)
        self.final_size_animation.setEndValue(new_size)

        if initial_pos:
            # When collapsing, set up move animation to happen at the same time to give the illusion of collapsing to the right
            self.move_animation.setStartValue(initial_pos)
            self.move_animation.setEndValue(self.get_position_for_size(new_size))
            self.move_animation.start()

            # Add name separator back in part way through
            QTimer.singleShot(self.move_animation.duration() * .75, self.name_separator.show)
        else:
            # When expanding, show bottom container part way through
            QTimer.singleShot(self.move_animation.duration() * .6, self.status_container.show)

        # Set up after final adjustment event handler
        self.final_size_animation.finished.connect(self.on_finished_size_adjustment)

        # Start final size adjustment animation
        self.final_size_animation.start()

    def on_finished_size_adjustment(self):
        # Reset handler on final size animation
        self.final_size_animation.finished.disconnect()

        # Make sure the name separator and status container ended in the right visibility
        if self.is_collapsing and not self.name_separator.isVisible() or self.is_collapsing and self.status_container.isVisible():
            self.collapse_widget()
        if self.is_expanding and self.name_separator.isVisible() or self.is_expanding and not self.status_container.isVisible():
            self.expand_widget()

        if not self.underMouse() and self.is_expanding:
            # If the widget was expanded, but the mouse is no longer over it, collapse the widget
            self.is_expanding = False
            self.is_collapsing = True
            QTimer.singleShot(1, lambda: self.expand_collapse_widget())
            return
        elif self.underMouse() and self.is_collapsing:
            # If the widget was collapsed, but the mouse is now over it, expand the widget
            self.is_collapsing = False
            self.is_expanding = True
            self.name_separator.hide()
            QTimer.singleShot(1, lambda: self.expand_collapse_widget())
            return

        # Ensure everything is sized and positioned properly
        if not self.underMouse():
            self.adjustSize()

        # Ensure widget is on screen
        if self.pos().x() > self.width() or self.pos().y() > self.height() or self.pos().x() < 0 or self.pos().y() < 0:
            self.move(self.get_position_for_size(self.size()))

        # Update resizing variables
        self.is_collapsing = False
        self.is_expanding = False


class TooltipWidget(QtWidgets.QWidget):
    def __init__(self, parent: QWidget, tooltip_widget: QWidget = None, name: str = None):
        super().__init__(parent)
        # Make sure we can receive mouse moving updates to detect when to show tooltip
        self.setMouseTracking(True)

        # Make sure tooltip widget is initialized
        self.tooltip_widget = tooltip_widget
        if not tooltip_widget:
            self.tooltip_widget = Label(name if name else "")
        self.tooltip_widget.setParent(UiObjects.current_screen.ui)
        self.tooltip_widget.hide()

        # The amount of change the mouse can move from showing the tooltip to hiding it
        self.mouse_move_tolerance: int = 2
        self.screen_buffer: int = 3
        self.mouse_entered: bool = False

        # Add a box shadow to tooltip widget
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        self.tooltip_widget.setGraphicsEffect(shadow)

        # Initialize variables for where/ when to show tooltip widget
        self.current_pos: QPoint = QPoint(0,0)
        self.local_pos: QPoint = QPoint(0,0)
        self.inactivity_timer: QTimer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.position_tooltip_widget)

        # Set styles of tooltip widget
        self.tooltip_widget.setStyleSheet(self.tooltip_widget.styleSheet() +
                                            "border: 2px solid" + UiObjects.dark_text_color + ";"
                                            "border-radius: 13%;"
                                            "background-color: " + UiObjects.light_text_color + ";")

    def enterEvent(self, event: QGraphicsSceneHoverEvent):
        self.mouse_entered = True
        self.update_local_pos(event.pos())
        self.update_current_cursor_pos()
        self.reset_inactivity_timer()
        super().enterEvent(event)

    def leaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.mouse_entered = False
        self.clear_tooltip_widget()
        super().leaveEvent(event)

    def reset_inactivity_timer(self):
        if self.inactivity_timer.isActive():
            self.inactivity_timer.stop()
        self.inactivity_timer.start(500)
        self.tooltip_widget.hide()

    def update_current_cursor_pos(self):
        self.current_pos = self.local_pos

    def current_pos_should_change(self) -> bool:
        is_x_in_tolerance: bool = self.is_in_tolerance(self.current_pos.x(), self.local_pos.x())
        is_y_in_tolerance: bool = self.is_in_tolerance(self.current_pos.y(), self.local_pos.y())
        return not is_x_in_tolerance or not is_y_in_tolerance

    def is_in_tolerance(self, current: int, test: int):
        return (current + self.mouse_move_tolerance) >= test >= (current - self.mouse_move_tolerance)

    def wheelEvent(self, event: QWheelEvent):
        self.clear_tooltip_widget()
        super().wheelEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Filter out any sub widget movement events that would throw off tooltip widget position
        if self.tooltip_widget.isVisible() and not self.is_stepped_mouse_move_event(event.pos()):
            super().mouseMoveEvent(event)
            return

        # Update new mouse location
        self.update_local_pos(event.pos())

        # If position should change (allow for buffer) and it's not shown, update the current position and reset the timer
        should_change: bool = self.current_pos_should_change()
        if not self.tooltip_widget.isVisible() or should_change:
            self.update_current_cursor_pos()
            self.reset_inactivity_timer()
        super().mouseMoveEvent(event)

    def clear_tooltip_widget(self):
        if self.inactivity_timer.isActive():
            self.inactivity_timer.stop()
        self.tooltip_widget.hide()

    def position_tooltip_widget(self):
        # If the widget is not being hovered over, hide the tooltip widget
        if not self.underMouse():
            self.tooltip_widget.hide()
            return

        # Update new height and width of tooltip widget
        width: int = UiObjects.current_screen.ui.width()
        height: int = UiObjects.current_screen.ui.height()
        self.tooltip_widget.setMaximumWidth((width/2) - self.screen_buffer)
        self.tooltip_widget.adjustSize()

        # Default move tooltip widget down and to the right
        x: int = 10
        y: int = 10

        # Cursor in the right half of app, move tooltip widget to the left of cursor
        if self.current_pos.x() > width/2:
            x = -self.tooltip_widget.width() - 10

        # Cursor in the bottom half of app, move tooltip widget to above the cursor
        if self.current_pos.y() > height/2:
            y = -self.tooltip_widget.height()

        # set new offset positon
        new_tooltip_position: QPoint = self.current_pos + QPoint(x, y)

        # Make sure the tool tip is fully on screen when shown
        if new_tooltip_position.x() < self.screen_buffer: # For when it's cut off on the left
            new_tooltip_position.setX(self.screen_buffer)
        if new_tooltip_position.y() < self.screen_buffer: # For when it's cut off from above
            new_tooltip_position.setY(self.screen_buffer)
        if new_tooltip_position.x() + self.tooltip_widget.width() + self.screen_buffer > width: # For when it's cut off on the right
            new_tooltip_position.setX(width - self.tooltip_widget.width() - self.screen_buffer)
        if new_tooltip_position.y() + self.tooltip_widget.height() + self.screen_buffer > height: # For when it's cut off from below
            new_tooltip_position.setY(height - self.tooltip_widget.height() - self.screen_buffer)

        # Move the tooltip, show it, and make sure everything fits in it
        self.tooltip_widget.move(new_tooltip_position)
        self.tooltip_widget.show()
        self.tooltip_widget.adjustSize()

    def update_local_pos(self, new_pos: QPoint):
        global_pos: QPoint = self.mapToGlobal(new_pos)
        self.local_pos = UiObjects.current_screen.ui.mapFromGlobal(global_pos)

    def is_stepped_mouse_move_event(self, new_pos: QPoint):
        # Ignore if the mouse just entered
        if self.mouse_entered:
            self.mouse_entered = False
            return True

        # Return true if new position is only a 1 pixel difference from old location
        global_pos: QPoint = self.mapToGlobal(new_pos)
        local_pos = UiObjects.current_screen.ui.mapFromGlobal(global_pos)
        return abs(abs(self.local_pos.x()) - abs(local_pos.x())) <= 1 and abs(abs(self.local_pos.y()) - abs(local_pos.y())) <= 1


class ItemTableCellActionedWidget(CenteredWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

class ItemTableCell(TooltipWidget):
    def __init__(self, name: str, graphics_scene: QGraphicsScene, tooltip_widget: QWidget = None, action_widget: QWidget = None, action_widget_button_text: str = None, name_label_font_size: int = 20, button_text: str = "Action", price: int = None, parent=None):
        if tooltip_widget:
            super().__init__(parent, tooltip_widget)
        else:
            super().__init__(parent, None, name)

        # Assign action widget (widget that will show when cell is clicked)
        if action_widget:
            self.action_widget = action_widget
        else:
            # Create default action widget
            label: Label = Label(name if name else "")
            okay: Button = Button("Okay")
            self.action_widget = QWidget()
            self.action_widget.setLayout(QVBoxLayout())
            self.action_widget.layout().addWidget(label)
            self.action_widget.layout().addWidget(okay)

        # Center action widget and add styles to it
        self.action_widget_container = CenteredFocusWidget(self.action_widget, 50, 75)
        self.action_widget.setStyleSheet("border: 2px solid" + UiObjects.dark_text_color + ";"
                                            "border-radius: 13%;"
                                            "background-color: " + UiObjects.light_text_color + ";")

        # Setup action widget buttons
        self.action_widget_button_layout = QHBoxLayout()
        if action_widget_button_text:
            # If there is an action widget button, set it up with click events that will run a customizable method then hide the action widget
            self.action_widget_button: Button = Button(action_widget_button_text)
            self.action_widget_button.clicked.connect(self.action_button_clicked)
            self.action_widget_button_layout.addWidget(self.action_widget_button)

            # Set up button to cancel out of the action button
            self.action_widget_back_button: Button = Button("Back")
        else:
            # If there is no action button, just create an okay button that acts as the back button
            self.action_widget_back_button: Button = Button("Okay")

        # Back button should just hide the action widget
        self.action_widget_back_button.clicked.connect(lambda: (
            self.action_widget_container.hide(),
            self.ui_loop.exit(True)
        ))

        # Add back button to button layout and the button layout to the action widget
        self.action_widget_button_layout.addWidget(self.action_widget_back_button)
        self.action_widget.layout().addLayout(self.action_widget_button_layout)

        # Set up loop for showing action widget
        self.ui_loop: QtCore.QEventLoop = QtCore.QEventLoop()

        # set up image for item table cell
        self.image: TransparentGraphicsView = TransparentGraphicsView()
        self.image.setScene(graphics_scene)
        self.image.mouseMoveEvent = self.mouseMoveEvent

        # Set up variables for item table cell (Item image, name label, action button, in that order top to bottom)
        self.pixmap_unscaled: QGraphicsPixmapItem = graphics_scene.items()[0]
        self.name: str = name
        self.name_label: Label = Label(name, name_label_font_size)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setMouseTracking(True)
        self.action: Button = Button(button_text, 10)
        self.action.setMouseTracking(True)

        # Add widgets to layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.action)

        # Set up styles for table cell
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget {border: 2px solid" + UiObjects.dark_text_color + ";"
                             "border-radius: 13%;}")
        self.image.setStyleSheet("border: 2px solid transparent;")
        self.name_label.setStyleSheet("border: 2px solid transparent; color: " + UiObjects.dark_text_color + ";")

        # Boolean for adding extra padding below table cell for more information about the table cell
        self.extra_info: bool = False

        # Receive events from app
        UiObjects.current_screen.ui.installEventFilter(self)

    # Signify that the user can click on the table cell, but changing the cursor image
    def enterEvent(self, event: QGraphicsSceneHoverEvent):
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        super().enterEvent(event)

    def leaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.action.underMouse() and event.button() == Qt.MouseButton.LeftButton:
            self.show_actioned_widget()

    def show_actioned_widget(self):
        self.action_widget_container.setParent(UiObjects.current_screen.ui)
        self.action_widget_container.show()
        self.action_widget_container.raise_()
        self.ui_loop.exec()

    # Custom event to run when action widget's action button is pressed returns true if action went through
    def on_action_button_triggered(self) -> bool:
        pass

    def action_button_clicked(self):
        if self.on_action_button_triggered():
            self.action_widget_container.hide()
            self.ui_loop.exit(True)


class WeaponItemTableCellType(Enum):
    VIEW = "View"
    SELECT = "Select"
    BUY = "Buy"
    SELL = "Sell"

class WeaponItemTableCell(ItemTableCell):
    def __init__(self, weapon: Weapon, player: Player, weapon_cell_type: WeaponItemTableCellType = WeaponItemTableCellType.VIEW, on_actioned_callback: Callable = None, name_label_font_size: int = 12, parent=None):
        # Variable for testing if dialog returns true or not
        self.message_result: bool = False

        # Set up class variables
        self.weapon = weapon
        self.weapon_price = weapon.price
        self.player = player
        self.weapon_cell_type = weapon_cell_type

        # Set up when function called when action button is pressed
        self.on_actioned_callback: Callable[[WeaponItemTableCell], None] = on_actioned_callback

        # Set up price of weapon
        self.price_color: str = ""
        if weapon_cell_type == WeaponItemTableCellType.BUY:
            self.price_color = self.get_price_color()
        elif weapon_cell_type == WeaponItemTableCellType.SELL:
            self.weapon_price = int(weapon.price / 2) # Weapons are sold at half price
        else:
            self.weapon_price = None

        # Get weapon image
        graphics_scene: QGraphicsScene = ImageUtil.load_image("weapons/" + weapon.weapon_image_name + ".png")

        # Set up tooltip and action widget
        tooltip_widget = self.create_main_widget(weapon, name_label_font_size, graphics_scene, False)
        action_widget = self.create_main_widget(weapon, name_label_font_size, graphics_scene)

        super().__init__(weapon.weapon_name, graphics_scene, tooltip_widget, action_widget, str(weapon_cell_type.value), name_label_font_size, str(weapon_cell_type.value), self.weapon_price, parent)

        # Set up on action button pressed (must be after super class is initialized, otherwise it will be overwritten)
        self.action.clicked.connect(self.action_button_clicked)

        # If we should show a price (for buying and selling weapons), set extra_info to true to provide buffer for it, then set up and add price label
        self.price_label: Label = None
        if self.weapon_price:
            self.extra_info = True
            self.price_label = Label(str(self.weapon_price) + " coins", int(name_label_font_size * .7))
            self.price_label.setStyleSheet("border: 2px solid transparent;" + self.price_color)
            self.price_label.setMouseTracking(True)
            self.player.property_change_listener.connect(self.player_property_updated)
            self.layout.addWidget(self.price_label)

    @staticmethod
    def get_color_based_on_selected(selected_value, value) -> str:
        match selected_value:
            case v if v < value:
                return "color: green"
            case v if v == value:
                return "color: white"
            case v if v > value:
                return "color: red"
        return None

    def on_action_button_triggered(self) -> bool:
        # Override method to handle presses for each type of weapon table cell type
        result: bool = False
        match self.weapon_cell_type:
            case WeaponItemTableCellType.BUY:
                result = self.do_weapon_buy()
            case WeaponItemTableCellType.SELL:
                result = self.do_weapon_sell()

        # If action went through (player said they were sure), run self.on_actioned_callback, passing this class
        if result:
            self.on_actioned_callback(self)

        return result

    def player_property_updated(self, name: str, _value: Any):
        if name == Player.money.fget.__name__:
            self.update_price_colors()

    def update_price_colors(self):
        if self.weapon_cell_type != WeaponItemTableCellType.BUY:
            return

        self.price_color = self.get_price_color()
        price_style = "border: 2px solid transparent;" + self.price_color

        action_widget_price_label: Label = self.action_widget.findChild(Label, "price_label")
        if action_widget_price_label:
            action_widget_price_label.setStyleSheet(price_style)

        if self.price_label:
            self.price_label.setStyleSheet(price_style)

    def get_price_color(self) -> str:
        if not self.weapon_price:
            return ""
        print(str(self.player.money) + " VS " + str(self.weapon_price))

        return "color: green" if self.player.money >= self.weapon_price else "color: red;"

    def do_weapon_sell(self) -> bool:
        # Handle player not having another weapon
        if len(self.player.weapons) <= 0:
            self.show_error_message("Sorry, you cannot sell your " + self.weapon.weapon_name + " because you must have at least one weapon.")
            return False

        if self.are_you_sure("Are you sure you want to sell your " + self.weapon.weapon_name + "?"):
            self.player.money = self.player.money + self.weapon_price
            return True
            # Player weapon objects will be handled later in the self.on_actioned_callback

        return False

    def do_weapon_buy(self) -> bool:
        # Handle player not having enough money
        if self.weapon_price > self.player.money:
            self.show_error_message("Sorry, you don't have enough coins to buy the " + self.weapon.weapon_name + ".")
            return False

        # Handle player not having enough strength
        if self.weapon.strength > self.player.strength:
            self.show_error_message("Sorry, you don't have enough strength to wield the " + self.weapon.weapon_name + ", so you cannot buy it.")
            return False

        # Make sure player is sure they want to buy the weapon
        if self.are_you_sure("Are you sure you want to buy the " + self.weapon.weapon_name + "?"):
            self.player.money = self.player.money - self.weapon_price
            return True
            # Player weapon objects will be handled later in the self.on_actioned_callback

        return False

    def are_you_sure(self, message: str) -> bool:
        return self.create_user_message(message)

    def show_error_message(self, message: str):
        return self.create_user_message(message, False)

    def create_user_message(self, message: str, is_sure: bool = True) -> bool:
        # Create a message label
        label = Label(message, 35)
        label.setStyleSheet("border: 2px solid transparent;" +
                            "color: " + UiObjects.dark_text_color + ";")

        # By default, create an okay button
        button = Button("Okay")

        # Set up message widget with label and button layout with button in it
        message_widget = QWidget()
        message_widget.setLayout(QVBoxLayout())
        message_widget.layout().addWidget(label)
        message_widget_button_layout = QHBoxLayout()
        message_widget.layout().addLayout(message_widget_button_layout)
        message_widget_button_layout.addWidget(button)
        message_widget.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        message_widget.setStyleSheet("border: 2px solid " + UiObjects.dark_text_color + ";"
                                            "border-radius: 13%;"
                                            "background-color: " + UiObjects.light_text_color + ";")

        # Center message dialog widget
        container = CenteredFocusWidget(message_widget, None, None, UiObjects.current_screen.ui)

        # Reinitialize dialog message result (only really needed for is_sure)
        self.message_result = False

        # Create loop for showing dialog message
        ui_loop = QEventLoop()

        # Add on click for main button
        button.clicked.connect(lambda: (
            self.set_message_result(True),
            container.hide(),
            ui_loop.exit(True)
        ))

        # If dialog type is is_sure
        if is_sure:
            # Change main button to 'Yes'
            button.setText("Yes")

            # Add second button 'No' that will result in a false result
            button_two = Button("No")
            button_two.clicked.connect(lambda: (
                self.set_message_result(False),
                container.hide(),
                ui_loop.exit(True)
            ))

            # Add second button to dialog message widget
            message_widget_button_layout.addWidget(button_two)

        # Show dialog message, and start loop to wait for result
        container.show()
        ui_loop.exec()

        # Return dialog message result
        return self.message_result

    def set_message_result(self, result):
        self.message_result = result

    def create_main_widget(self, weapon: Weapon, name_label_font_size: int, graphics_scene: QGraphicsScene, is_action_widget: bool = True):
        # Initialize widget
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        # Create weapon image widget
        image: TransparentGraphicsView = TransparentGraphicsView()
        image.setScene(graphics_scene)
        image.setFixedHeight(UiObjects.current_screen.ui.height()/5)
        widget.layout().addWidget(image)

        # Create name label and add to widget
        label_styles: str = "border: 2px solid transparent;"
        name_label: Label = Label(weapon.weapon_name, name_label_font_size)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setMouseTracking(True)
        name_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";" 
                                    "border-bottom: 2px solid " + UiObjects.dark_text_color + ";"
                                    "border-radius: 0")
        widget.layout().addWidget(name_label)

        # Create damage label and add to widget
        damage_label: Label = Label("Damage:", name_label_font_size-4)
        damage_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";")
        damage_amount_label: Label = Label(str(weapon.damage), name_label_font_size-4)
        damage_color: str = self.get_color_based_on_selected(self.player.selected_weapon.damage, weapon.damage)
        damage_amount_label.setStyleSheet(label_styles + damage_color)
        damage_container: QHBoxLayout = QHBoxLayout()
        damage_container.addWidget(damage_label)
        damage_container.addWidget(damage_amount_label)
        widget.layout().addLayout(damage_container)

        # Create attack rate label and add to widget
        attack_rate_label: Label = Label("Attack Rate:", name_label_font_size-4)
        attack_rate_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";")
        attack_rate_amount_label: Label = Label(str(weapon.attack_rate), name_label_font_size-4)
        attack_rate_color: str = self.get_color_based_on_selected(self.player.selected_weapon.attack_rate, weapon.attack_rate)
        attack_rate_amount_label.setStyleSheet(label_styles + attack_rate_color)
        attack_rate_container: QHBoxLayout = QHBoxLayout()
        attack_rate_container.addWidget(attack_rate_label)
        attack_rate_container.addWidget(attack_rate_amount_label)
        widget.layout().addLayout(attack_rate_container)

        # Create strength label and add to widget
        strength_label: Label = Label("Strength Required:", name_label_font_size-4)
        strength_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";")
        strength_amount_label: Label = Label(str(weapon.strength), name_label_font_size-4)
        strength_color: str = "" if self.player.strength >= weapon.strength else "color: red;"
        strength_amount_label.setStyleSheet(label_styles + strength_color)
        strength_container: QHBoxLayout = QHBoxLayout()
        strength_container.addWidget(strength_label)
        strength_container.addWidget(strength_amount_label)
        widget.layout().addLayout(strength_container)

        if self.weapon_price and is_action_widget:
            # If this is a buy or sell weapon table cell and we are creating the action widget, add a 'current money amount' +/- 'weapon price' = 'new money amount' label
            operand: str = "-" if self.weapon_cell_type == WeaponItemTableCellType.BUY else "+"
            new_total: int = (self.player.money - self.weapon_price) if self.weapon_cell_type == WeaponItemTableCellType.BUY else (self.player.money + self.weapon_price)
            new_price_label: Label = Label("Current: " + str(self.player.money) + " " + operand + " Price: " + str(self.weapon_price) + " = New Total: " + str(new_total) + " coins", name_label_font_size-4)
            new_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_price_label.setStyleSheet(label_styles + self.price_color)
            new_price_label.setObjectName("price_label")
            widget.layout().addWidget(new_price_label)

        widget.adjustSize()

        return widget


class ItemTableView(QtWidgets.QScrollArea):
    def __init__(self, row_height_divisor: int = 3, column_count: int = 3, parent=None):
        super().__init__(parent)
        # Initialize item variables
        self.row_height_devisor = row_height_divisor
        self.column_count: int = column_count
        self.items: list[ItemTableCell] = []

        # Initialize table
        self.table_container = QWidget()
        self.table_container.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.table_container.setStyleSheet("border: 2px solid transparent; background-color: transparent;")
        self.table_layout = QGridLayout(self.table_container)
        self.table_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add table to self (to scroll area with no horizontal scroll bar)
        self.setAlignment(Qt.AlignCenter)
        self.setWidget(self.table_container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up styles
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget {background-color: " + UiObjects.get_transparent_light_background_color(200) + ";"
                             "border: 2px solid" + UiObjects.dark_text_color + ";"
                             "border-radius: 13%;}")

        # Accept events
        UiObjects.current_screen.ui.installEventFilter(self)

    def add_item(self, item: ItemTableCell):
        # Set image width
        width: int = self.rect().width()
        height: int = self.rect().height()

        # Set up item sizes
        item.image.setMinimumHeight(height/self.row_height_devisor * 3/4)
        item.action.setMinimumHeight(39) # Button text sometimes got cut off
        item.setMaximumWidth(width/self.column_count)
        item.setMinimumWidth(QFontMetrics(item.action.font()).horizontalAdvance(item.action.text())+40) # Width based on action text size

        # Connect signal to refresh all items
        # item.item_table_cell_ui_update_request.connect(self.update_all_item_ui)

        # Add item
        self.items.append(item)
        self.table_layout.addWidget(item, self.table_layout.count() // self.column_count, self.table_layout.count() % self.column_count)

    def remove_item(self, item: ItemTableCell):
        # Remove the widget from the layout and delete it
        self.table_layout.removeWidget(item)
        item.deleteLater()
        self.items.remove(item)

        # Rearrange the remaining widgets
        # First, clear the layout items
        for i in reversed(range(self.table_layout.count())):
            item = self.table_layout.takeAt(i)
            if item.widget() is not None:
                # We don't delete the widget again, it's already in the widget_list
                pass
            elif item.layout() is not None:
                # Handle nested layouts if needed
                pass
            del item  # delete the layout item

        # Re-add all existing widgets from the updated list
        for i, item in enumerate(self.items):
            self.table_layout.addWidget(item, i // self.column_count, i % self.column_count)

    def eventFilter(self, source: QWidget, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.resize_item_image()
        return super().eventFilter(source, event)

    def resize_item_image(self):
        # Get current size
        width: int = self.rect().width()
        height: int = self.height()

        for item in self.items:
            item.image.setMaximumHeight(height/self.row_height_devisor * 3/4)
            item.image.setMinimumHeight(height/self.row_height_devisor * 3/4)
            item.setMaximumWidth(width/self.column_count-15)
            extra_divisor: float = 1.3 if item.extra_info else 1.7 # Extra padding if more info on the bottom
            extra_padding: int = height/self.row_height_devisor*5/8 if self.column_count >= len(self.items) and width >= 462 else height/self.row_height_devisor/extra_divisor # Extra padding for one row tables, add extra when width is smaller
            item.setMaximumHeight(height/self.row_height_devisor + extra_padding)

    # def player_property_updated(self, name: str, value: Any):
        # print(name + " changed")
        # if name == Player.money.fget.__name__:
        #     self.update_all_item_ui(name, value)


class Screen(QWidget):
    def __init__(self, screen_name: str = None):
        super().__init__()
        self.pixmap_unscaled: QPixmap = None
        if screen_name is None:
            screen_name = self.camel_to_snake(self.__class__.__name__)
        self.screen_name = screen_name
        self.screen_image_location = "screens/" + screen_name + "/"
        self.previous_screen: Screen = None
        self.has_back_button: bool = False

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

    def set_up_background_image(self, pixmap: QPixmap):
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

    def on_back_button_clicked(self):
        pass


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
        self.highlight_pen = QPen(
            QColor(UiObjects.highlight_color), font_size / 6,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )

        # Show location label and location outline
        self.location_label.setVisible(True)
        self._is_hovered = True
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        # Hide location label and remove location outline
        self.location_label.setVisible(False)
        self._is_hovered = False
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
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
        return "map_locations/" + image_name

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
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app: QApplication = QApplication(sys.argv)
    window: GameWindow = GameWindow()
    current_screen: Screen = None
    old_screen: Screen = None
    light_text_color: str = "#EAAB08"
    dark_text_color: str = "#6B3F02"
    highlight_color: str = "gold"
    font_name: str = "Harrington"

    @staticmethod
    def get_transparent_light_background_color(opacity: int):
        return "rgba(234, 171, 8, " + str(opacity) + ");"
