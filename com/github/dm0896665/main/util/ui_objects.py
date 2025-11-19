import math
import re
import sys
from enum import Enum
from typing import Callable

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QEvent, QPoint, Qt, QSignalBlocker, QObject, QPointF, QSize, QPropertyAnimation, QEventLoop, \
    QTimer, Signal
from PySide6.QtGui import QPalette, QResizeEvent, QPixmap, QColor, QPen, QFont, QTextCursor, QTextCharFormat, QBrush, \
    QRadialGradient, QPainter, QCursor, QFontMetrics, QPainterPath, QIcon, QMouseEvent, QWheelEvent

from PySide6.QtWidgets import QApplication, QGridLayout, QWidget, QMainWindow, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView, QGraphicsSceneHoverEvent, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsOpacityEffect, QVBoxLayout, QGraphicsSceneMoveEvent, QGraphicsDropShadowEffect, QLayout, QHBoxLayout

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
        self.center_widget_width_percent = center_widget_width_percent
        self.center_widget_height_percent = center_widget_height_percent

        self.center_widget: QWidget = center_widget
        self.resize_center_widget()

        self.centered_widget_container_h = QWidget()
        self.centered_widget_container_h.setLayout(QHBoxLayout())
        self.centered_widget_container_h.layout().addWidget(self.center_widget)
        self.centered_widget_container_h.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centered_widget_container_h.setStyleSheet("background-color: transparent;")

        self.centered_widget_container_v = QWidget()
        self.centered_widget_container_v.setLayout(QVBoxLayout())
        self.centered_widget_container_v.layout().addWidget(self.centered_widget_container_h)
        self.centered_widget_container_v.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centered_widget_container_v.setStyleSheet("background-color: transparent;")

        self.setFixedWidth(UiObjects.current_screen.ui.width())
        self.setFixedHeight(UiObjects.current_screen.ui.height())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.centered_widget_container_v)
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet("QWidget {background-color: rgba(64,64,64,.64);}")

        UiObjects.current_screen.ui.installEventFilter(self)

    def eventFilter(self, source: QWidget, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.setFixedWidth(UiObjects.current_screen.ui.width())
            self.setFixedHeight(UiObjects.current_screen.ui.height())

            self.resize_center_widget()
        return super().eventFilter(source, event)

    def resize_center_widget(self):
        if self.center_widget_width_percent is None or self.center_widget_height_percent is None:
            self.center_widget.adjustSize()
        else:
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
        self.fitInView(self.sceneRect(), aspectRadioMode=Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

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
        self.width_percentage: int = width_percentage
        self.height_percentage: int = height_percentage
        self.original_pixmap = ImageUtil.load_image_map("map_locations/back.png")
        self.back_image: QGraphicsPixmapItem = QGraphicsPixmapItem(self.original_pixmap)
        self.back_image_highlighted: QGraphicsPixmapItem = QGraphicsPixmapItem(self.original_pixmap)
        self.back_image_highlighted.setShapeMode(QGraphicsPixmapItem.MaskShape)

        highlight_pen = QPen(
                QColor(UiObjects.highlight_color), max(16, UiObjects.window.width() // 40/2),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
        highlight_pen.setJoinStyle(Qt.RoundJoin)
        painter = QPainter(self.original_pixmap)
        painter.setPen(highlight_pen)
        painter.setBrush(Qt.NoBrush)
        outline_path = self.back_image.shape()
        painter.drawPath(outline_path)
        painter.end()

        # self.setToolTip("Back")
        # self.setIcon(QIcon(self.back_image))
        # self.setIconSize(self.get_size())
        # self.adjustSize()
        # self.setStyleSheet("background-color: transparent;"
        #                     "border: 1px solid transparent;")
        # self.move(5, 5)
        # self.show()
        self.button = QtWidgets.QPushButton()
        self.button.setIcon(QIcon(self.back_image.pixmap()))
        self.button.setIconSize(self.get_size())
        self.button.setMouseTracking(True)
        self.button.installEventFilter(self)
        self.button.clicked.connect(on_click)
        UiObjects.window.installEventFilter(self)
        self.hover_label = OutlinedLabel("Back", 30, UiObjects.highlight_color)
        self.hover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_policy = self.hover_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.hover_label.setSizePolicy(size_policy)
        self.hover_label.hide()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.button)
        layout.addWidget(self.hover_label)
        self.adjustSize()
        self.setStyleSheet("background-color: transparent;"
                            "border: 1px solid transparent;")
        self.move(5, 5)

    def eventFilter(self, source: QWidget, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.button.setIconSize(self.get_size())
            self.button.adjustSize()
            self.adjustSize()

        if source == self.button:
            if event.type() == QEvent.Type.Enter:
                self.set_button_icon(self.original_pixmap)
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
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))
        super().resizeEvent(event)

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

    def resizeEvent(self, event):
        font_size = max(12, UiObjects.window.width() // self.window_size_divisor)
        self.setFont(QFont(UiObjects.font_name, font_size))
        super().resizeEvent(event)


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
        font_size = max(16, UiObjects.window.width() // 60)
        self.setFont(QFont(UiObjects.font_name, font_size))
        super().resizeEvent(event)

class TooltipWidget(QtWidgets.QWidget):
    def __init__(self, parent: QWidget, tooltip_widget: QWidget = None, name: str = None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self.tooltip_widget = tooltip_widget
        if not tooltip_widget:
            self.tooltip_widget = Label(name if name else "")
        self.tooltip_widget.setParent(UiObjects.current_screen.ui)
        self.tooltip_widget.hide()

        # The amount of change the mouse can move from showing the tooltip to hiding it
        self.mouse_move_tolerance: int = 2
        self.screen_buffer: int = 3
        self.mouse_entered: bool = False

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        self.tooltip_widget.setGraphicsEffect(shadow)

        self.current_pos: QPoint = QPoint(0,0)
        self.local_pos: QPoint = QPoint(0,0)
        self.inactivity_timer: QTimer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.position_tooltip_widget)

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
        if self.tooltip_widget.isVisible() and not self.is_stepped_mouse_move_event(event.pos()):
            super().mouseMoveEvent(event)
            return
        self.update_local_pos(event.pos())
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
        if not self.underMouse():
            self.tooltip_widget.hide()
            return
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
        if self.mouse_entered:
            self.mouse_entered = False
            return True

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

        if action_widget:
            self.action_widget = action_widget
        else:
            label: Label = Label(name if name else "")
            okay: Button = Button("Okay")
            self.action_widget = QWidget()
            self.action_widget.setLayout(QVBoxLayout())
            self.action_widget.layout().addWidget(label)
            self.action_widget.layout().addWidget(okay)

        self.action_widget_container = CenteredFocusWidget(action_widget, 50, 75)
        self.action_widget.setStyleSheet("border: 2px solid" + UiObjects.dark_text_color + ";"
                                            "border-radius: 13%;"
                                            "background-color: " + UiObjects.light_text_color + ";")
        self.action_widget_button_layout = QHBoxLayout()
        if action_widget_button_text:
            self.action_widget_button: Button = Button(action_widget_button_text)
            self.action_widget_button.clicked.connect(lambda: (
                self.on_action_widget_button_triggered(),
                self.action_widget_container.hide(),
                self.ui_loop.exit(True)
            ))
            self.action_widget_button_layout.addWidget(self.action_widget_button)
            self.action_widget_back_button: Button = Button("Back")
        else:
            self.action_widget_back_button: Button = Button("Okay")

        self.action_widget_back_button.clicked.connect(lambda: (
            self.action_widget_container.hide(),
            self.ui_loop.exit(True)
        ))
        self.action_widget_button_layout.addWidget(self.action_widget_back_button)
        self.action_widget.layout().addLayout(self.action_widget_button_layout)
        self.ui_loop: QtCore.QEventLoop = QtCore.QEventLoop()

        self.image: TransparentGraphicsView = TransparentGraphicsView()
        self.image.setScene(graphics_scene)
        self.image.mouseMoveEvent = self.mouseMoveEvent

        self.pixmap_unscaled: QGraphicsPixmapItem = graphics_scene.items()[0]
        self.name: str = name
        self.name_label: Label = Label(name, name_label_font_size)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setMouseTracking(True)
        self.action: Button = Button(button_text, 10)
        self.action.setMouseTracking(True)
        self.price_label: Label = None

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.action)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget {border: 2px solid" + UiObjects.dark_text_color + ";"
                             "border-radius: 13%;}")
        self.image.setStyleSheet("border: 2px solid transparent;")
        self.name_label.setStyleSheet("border: 2px solid transparent; color: " + UiObjects.dark_text_color + ";")

        self.extra_info: bool = False

        UiObjects.current_screen.ui.installEventFilter(self)

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

    def on_action_widget_button_triggered(self):
        pass


class WeaponItemTableCellType(Enum):
    VIEW = "View"
    SELECT = "Select"
    BUY = "Buy"
    SELL = "Sell"

class WeaponItemTableCell(ItemTableCell):
    def __init__(self, weapon: Weapon, player: Player, weapon_cell_type: WeaponItemTableCellType = WeaponItemTableCellType.VIEW, on_actioned_callback: Callable = None, name_label_font_size: int = 12, parent=None):
        self.message_result: bool = False
        self.on_actioned_callback: Callable[[WeaponItemTableCell, bool], None] = on_actioned_callback
        price: int = None
        self.price_color: str = ""
        if weapon_cell_type == WeaponItemTableCellType.BUY:
            price = weapon.price
            self.price_color = "color: green" if player.money >= price else "color: red;"
        elif weapon_cell_type == WeaponItemTableCellType.SELL:
            price = int(weapon.price / 2)

        self.weapon = weapon
        self.weapon_price = price
        self.player = player
        self.weapon_cell_type = weapon_cell_type

        graphics_scene: QGraphicsScene = ImageUtil.load_image("weapons/" + weapon.weapon_image_name + ".png")

        tooltip_widget = self.create_main_widget(weapon, name_label_font_size, graphics_scene, False)
        actioned_widget = self.create_main_widget(weapon, name_label_font_size, graphics_scene)

        super().__init__(weapon.weapon_name, graphics_scene, tooltip_widget, actioned_widget, str(weapon_cell_type.value), name_label_font_size, str(weapon_cell_type.value), price, parent)
        self.action.clicked.connect(self.on_action_widget_button_triggered)

        if price:
            self.extra_info = True
            self.price_label: Label = Label(str(price) + " coins", int(name_label_font_size * .7))
            self.price_label.setStyleSheet("border: 2px solid transparent;" + self.price_color)
            self.price_label.setMouseTracking(True)
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

    def on_action_widget_button_triggered(self):
        result: bool = False
        match self.weapon_cell_type:
            case WeaponItemTableCellType.BUY:
                result = self.do_weapon_buy()
            case WeaponItemTableCellType.SELL:
                result = self.do_weapon_sell()

        self.on_actioned_callback(self, result)

    def do_weapon_sell(self) -> bool:
        if self.are_you_sure("Are you sure you want to sell your " + self.weapon.weapon_name + "?"):
            self.player.money = self.player.money + self.weapon_price
            return True
            # Player weapon objects will be handled later in the callback

        return False

    def do_weapon_buy(self) -> bool:
        if self.weapon_price > self.player.money:
            self.show_error_message("Sorry, you don't have enough coins to buy the " + self.weapon.weapon_name + ".")
            return False

        if self.weapon.strength > self.player.strength:
            self.show_error_message("Sorry, you don't have enough strength to wield the " + self.weapon.weapon_name + ", so you cannot buy it.")
            return False

        if self.are_you_sure("Are you sure you want to buy the " + self.weapon.weapon_name + "?"):
            self.player.money = self.player.money - self.weapon_price
            return True
            # Player weapon objects will be handled later in the callback

        return False

    def are_you_sure(self, message: str) -> bool:
        return self.create_user_message(message)

    def show_error_message(self, message: str):
        return self.create_user_message(message, False)

    def create_user_message(self, message: str, is_sure: bool = True) -> bool:
        label = Label(message, 35)
        label.setStyleSheet("border: 2px solid transparent;" +
                            "color: " + UiObjects.dark_text_color + ";")
        button = Button("Okay")
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
        container = CenteredFocusWidget(message_widget, None, None, UiObjects.current_screen.ui)
        self.message_result = False
        ui_loop = QEventLoop()
        button.clicked.connect(lambda: (
            self.set_message_result(True),
            container.hide(),
            ui_loop.exit(True)
        ))

        if is_sure:
            button.setText("Yes")
            button_two = Button("No")
            button_two.clicked.connect(lambda: (
                self.set_message_result(False),
                container.hide(),
                ui_loop.exit(True)
            ))
            message_widget_button_layout.addWidget(button_two)

        container.show()
        ui_loop.exec()

        return self.message_result

    def set_message_result(self, result):
        self.message_result = result

    def create_main_widget(self, weapon: Weapon, name_label_font_size: int, graphics_scene: QGraphicsScene, is_action_widget: bool = True):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        image: TransparentGraphicsView = TransparentGraphicsView()
        image.setScene(graphics_scene)
        image.setFixedHeight(UiObjects.current_screen.ui.height()/5)
        widget.layout().addWidget(image)

        label_styles: str = "border: 2px solid transparent;"
        name_label: Label = Label(weapon.weapon_name, name_label_font_size)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setMouseTracking(True)
        name_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";" 
                                    "border-bottom: 2px solid " + UiObjects.dark_text_color + ";"
                                    "border-radius: 0")
        widget.layout().addWidget(name_label)

        damage_label: Label = Label("Damage:", name_label_font_size-4)
        damage_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";")
        damage_amount_label: Label = Label(str(weapon.damage), name_label_font_size-4)
        damage_color: str = self.get_color_based_on_selected(self.player.selected_weapon.damage, weapon.damage)
        damage_amount_label.setStyleSheet(label_styles + damage_color)
        damage_container: QHBoxLayout = QHBoxLayout()
        damage_container.addWidget(damage_label)
        damage_container.addWidget(damage_amount_label)
        widget.layout().addLayout(damage_container)

        attack_rate_label: Label = Label("Attack Rate:", name_label_font_size-4)
        attack_rate_label.setStyleSheet(label_styles + "color: " + UiObjects.dark_text_color + ";")
        attack_rate_amount_label: Label = Label(str(weapon.attack_rate), name_label_font_size-4)
        attack_rate_color: str = self.get_color_based_on_selected(self.player.selected_weapon.attack_rate, weapon.attack_rate)
        attack_rate_amount_label.setStyleSheet(label_styles + attack_rate_color)
        attack_rate_container: QHBoxLayout = QHBoxLayout()
        attack_rate_container.addWidget(attack_rate_label)
        attack_rate_container.addWidget(attack_rate_amount_label)
        widget.layout().addLayout(attack_rate_container)

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
            operand: str = "-" if self.weapon_cell_type == WeaponItemTableCellType.BUY else "+"
            new_total: int = (self.player.money - self.weapon_price) if self.weapon_cell_type == WeaponItemTableCellType.BUY else (self.player.money + self.weapon_price)
            new_price_label: Label = Label("Current: " + str(self.player.money) + " " + operand + " Price: " + str(self.weapon_price) + " = New Total: " + str(new_total) + " coins", name_label_font_size-4)
            new_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_price_label.setStyleSheet(label_styles + self.price_color)
            widget.layout().addWidget(new_price_label)

        widget.adjustSize()

        return widget


class ItemTableView(QtWidgets.QScrollArea):
    def __init__(self, row_height_divisor: int = 3, column_count: int = 3, parent=None):
        super().__init__(parent)
        self.row_height_devisor = row_height_divisor
        self.column_count: int = column_count
        self.row: int = 0
        self.col: int = 0
        self.items: list[ItemTableCell] = []

        self.table_container = QWidget()
        self.table_container.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.table_container.setStyleSheet("border: 2px solid transparent; background-color: transparent;")
        self.table_layout = QGridLayout(self.table_container)
        self.table_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setAlignment(Qt.AlignCenter)
        self.setWidget(self.table_container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget {background-color: " + UiObjects.light_text_color + ";"
                             "border: 2px solid" + UiObjects.dark_text_color + ";"
                             "border-radius: 13%;}")

        UiObjects.current_screen.ui.installEventFilter(self)

    def add_item(self, item: ItemTableCell):
        # Set image width
        width: int = self.rect().width()
        height: int = self.rect().height()
        # item.image.setFixedHeight(height/self.row_height_devisor)
        item.image.setMinimumHeight(height/self.row_height_devisor * 3/4)
        item.action.setMinimumHeight(39)
        item.setMaximumWidth(width/self.column_count)
        item.setMinimumWidth(QFontMetrics(item.action.font()).horizontalAdvance(item.action.text())+40)
        # item.setMaximumHeight(height/self.row_height_devisor + height/self.row_height_devisor/20)

        # Add item
        self.items.append(item)
        self.table_layout.addWidget(item, self.row, self.col)

        # Update position to next open space
        # If there's no more open columns, go to next row
        self.col+= 1
        if self.col == self.column_count:
            self.col = 0
            self.row+= 1

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
        for i, widget in enumerate(self.items):
            self.table_layout.addWidget(widget, i // self.column_count, i % self.column_count)

        if self.col == 0:
            self.col = self.column_count
            self.row-= 1
        else:
            self.col -= 1

    def eventFilter(self, source: QWidget, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.resize_item_image()
        return super().eventFilter(source, event)

    def resize_item_image(self):
        width: int = self.rect().width()
        height: int = self.height()
        for item in self.items:
            # scaled_pixmap = item.pixmap_unscaled.scaled(width/self.column_count, width/self.column_count,
            #                                        Qt.AspectRatioMode.KeepAspectRatio,
            #                                        Qt.TransformationMode.SmoothTransformation)
            # item.image.scene().items()[0].setPixmap(scaled_pixmap)
            # item.image.setFixedWidth(width/self.column_count)
            item.image.setFixedHeight(height/self.row_height_devisor * 3/4)
            item.setMaximumWidth(width/self.column_count-15)
            extra_divisor: float = 1.3 if item.extra_info else 1.7
            extra_padding: int = height/self.row_height_devisor*5/8 if self.column_count >= len(self.items) else height/self.row_height_devisor/extra_divisor
            item.setMaximumHeight(height/self.row_height_devisor + extra_padding)
            # item.image.fitInView(item.image.sceneRect(), aspectRadioMode=Qt.AspectRatioMode.KeepAspectRatio)


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
