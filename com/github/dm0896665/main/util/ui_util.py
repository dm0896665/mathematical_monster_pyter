from PySide6 import QtCore, QtUiTools
import sys

from PySide6.QtCore import QTimer, QPropertyAnimation, QEventLoop
from PySide6.QtGui import QImage, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsScene, QWidget, QGraphicsView, \
    QGraphicsOpacityEffect

from com.github.dm0896665.main.util.custom_ui_widgets import CustomGraphicsView
from com.github.dm0896665.main.util.ui_objects import UiObjects, Screen


class UiUtil:
    loader: QtUiTools.QUiLoader = QtUiTools.QUiLoader()
    loader.registerCustomWidget(CustomGraphicsView)

    @staticmethod
    def load_ui_screen(ui_screen_name, parent=None):
        return UiUtil.load_ui_widget('screens/' + ui_screen_name, parent)

    @staticmethod
    def load_ui_prompt(parent=None):
        return UiUtil.load_ui_widget('prompt', parent)

    @staticmethod
    def load_ui_widget(ui_file_name, parent=None):
        if not sys.path[0].endswith('ui'):
            ui_file_name = "com/github/dm0896665/main/ui/" + ui_file_name
        ui_file = QtCore.QFile(ui_file_name + '.ui')
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = UiUtil.loader.load(ui_file, parent)
        ui_file.close()
        return ui

    @staticmethod
    def load_player_image(image_file_name, graphics_view=None):
        return UiUtil.load_image('player/' + image_file_name + ".png", graphics_view)

    @staticmethod
    def load_monster_image(image_file_name, graphics_view=None):
        return UiUtil.load_image('monsters/' + image_file_name + ".png", graphics_view)

    @staticmethod
    def load_image(image_file_name, graphics_view: QGraphicsView=None) -> QGraphicsScene:
        pic: QGraphicsPixmapItem = QGraphicsPixmapItem()
        pic.setTransformationMode(QtCore.Qt.SmoothTransformation)

        image_map: QGraphicsPixmapItem = UiUtil.load_image_map(image_file_name)
        if image_map is None:
            return None

        pic.setPixmap(image_map)

        scene: QGraphicsScene = QGraphicsScene()
        scene.addItem(pic)

        if graphics_view is not None:
            graphics_view.setScene(scene)

        return scene

    @staticmethod
    def load_image_map(image_file_name) -> QGraphicsPixmapItem:
        if not sys.path[0].endswith('images'):
            image_file_name = "com/github/dm0896665/resources/images/" + image_file_name

        image_qt: QImage = QImage()
        image_loaded: bool = image_qt.load(image_file_name)

        if not image_loaded:
            return None

        return QPixmap.fromImage(image_qt)

    @staticmethod
    def change_screen(new_screen: Screen):
        ui = UiUtil.load_ui_screen(new_screen.screen_name, new_screen)
        new_screen.ui = ui
        UiUtil.do_change_screen(new_screen) #switchable
        # Worker(UiUtil.do_change_screen, new_screen).start() #switchable
        # thread: QThread = QThread()
        # change_screen_worker.moveToThread(thread)
        # thread.started.connect(change_screen_worker.run)
        # change_screen_worker.signals.finished.connect(thread.quit)
        # change_screen_worker.signals.finished.connect(change_screen_worker.deleteLater)
        # change_screen_worker.signals.finished.connect(thread.deleteLater)
        # thread.start()

    @staticmethod
    def do_change_screen(new_screen: Screen):
        UiObjects.old_screen: Screen = UiObjects.current_screen
        if UiObjects.old_screen is not None:
            UiObjects.old_screen.on_screen_will_hide()

        new_screen.setParent(UiObjects.window)
        #ui = UiUtil.load_ui_screen(new_screen.screen_name, new_screen)
        #new_screen.ui = ui
        new_screen.ui.setParent(new_screen)
        new_screen.on_screen_will_show()

        UiUtil.setCentralWidget(new_screen.ui)
        UiObjects.current_screen = new_screen

        if UiObjects.old_screen is not None:
            UiObjects.old_screen.on_screen_did_hide()

        new_screen.ui.installEventFilter(new_screen)

        # Set background image
        image_path: str = "screens/" + new_screen.screen_name + "/background.png"
        background_map: QGraphicsPixmapItem = UiUtil.load_image_map(image_path)
        if background_map is not None:
            new_screen.set_up_background_image(background_map)
        else:
            # Reset background, otherwise the last screen's background will show
            palette: QPalette = QPalette()
            palette.setColor(QPalette.Window, QColor(77, 77, 77, 100))
            new_screen.parent().setPalette(palette)

        new_screen.on_screen_did_show()

    @staticmethod
    def setCentralWidget(widget: QWidget | Screen):
        if isinstance(widget, Screen):
            widget = widget.ui
        UiObjects.window.setCentralWidget(widget)
        QApplication.processEvents()

    @staticmethod
    def toggle_visibility(widget: QWidget, duration: int=250):
        opacity_effect = QGraphicsOpacityEffect(widget, opacity=1.0)
        widget.setGraphicsEffect(opacity_effect)
        fade_in_and_out_animation = QPropertyAnimation(
            widget,
            propertyName=b"opacity",
            targetObject=opacity_effect,
            duration=duration,
            startValue=0.0,
            endValue=1.0,
        )
        loop = QEventLoop()

        if widget.isVisible():
            # Hide animation
            widget.show()
            fade_in_and_out_animation.finished.connect(loop.quit)
            fade_in_and_out_animation.setDirection(QPropertyAnimation.Backward)
            fade_in_and_out_animation.start()
            loop.exec_()
        else:
            # Show animation
            widget.show()
            fade_in_and_out_animation.finished.connect(loop.quit)
            fade_in_and_out_animation.setDirection(QPropertyAnimation.Forward)
            fade_in_and_out_animation.start()
            loop.exec_()

    @staticmethod
    def show_widget_for_duration(widget: QWidget, duration: int):
        widget.setParent(UiObjects.current_screen.ui)
        loop: QtCore.QEventLoop = QtCore.QEventLoop()
        QTimer.singleShot(duration * 1000, lambda: UiUtil.stop_show_widget_for_duration(widget, loop))

        UiUtil.toggle_visibility(widget)
        widget.raise_()
        loop.exec()

    @staticmethod
    def stop_show_widget_for_duration(widget: QWidget, loop: QtCore.QEventLoop):
        UiUtil.toggle_visibility(widget)
        # widget.deleteLater()
        loop.exit(True)