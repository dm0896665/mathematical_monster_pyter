import inspect
import os

from PySide6 import QtCore, QtUiTools
import sys

from PySide6.QtCore import QTimer, QPropertyAnimation, QEventLoop
from PySide6.QtGui import QPalette, QColor, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem, QWidget, QGraphicsOpacityEffect

from com.github.dm0896665.main.util.image_util import ImageUtil
from com.github.dm0896665.main.util.ui_objects import UiObjects, Screen, MapScreen, BackButton


# Gets all custom widget classes from custom_ui_widgets.py such as CustomGraphicsView, Button, etc.
def get_custom_widget_classes():
    file_path = 'com/github/dm0896665/main/util/custom_ui_widgets.py'

    # Add the directory containing the file to sys.path so it can be imported
    sys.path.insert(0, os.path.dirname(os.path.abspath(file_path)))

    # Import the module dynamically
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        module = __import__(module_name)
    except ImportError as e:
        print(f"Error importing module '{module_name}': {e}")
        sys.exit(1)

    # Get all members of the module
    all_members = inspect.getmembers(module)

    # Filter for classes defined within that module
    return [
        obj for name, obj in all_members
        if inspect.isclass(obj) and obj.__module__ == module_name
    ]


class UiUtil:
    # Custom widgets need to be registered to be used in .ui files
    custom_widgets = get_custom_widget_classes()
    loader: QtUiTools.QUiLoader = QtUiTools.QUiLoader()
    for custom_widget in custom_widgets:
        loader.registerCustomWidget(custom_widget)

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
        # Only set the new screen's previous screen if we are going forward a screen (as previous screen is used to go back to the previous screen)
        if not new_screen.previous_screen or UiObjects.old_screen.screen_name != new_screen.screen_name:
            new_screen.previous_screen = UiObjects.current_screen

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
        image_path: str = new_screen.screen_image_location + "background.png"
        background_map: QPixmap = ImageUtil.load_image_map(image_path)
        if background_map is not None:
            new_screen.set_up_background_image(background_map)
        else:
            # Reset background, otherwise the last screen's background will show
            palette: QPalette = QPalette()
            palette.setColor(QPalette.Window, QColor(77, 77, 77, 100))
            new_screen.parent().setPalette(palette)

        new_screen.init_ui()
        if new_screen.has_back_button:
            if Screen.on_back_button_clicked != new_screen.__class__.on_back_button_clicked:
                BackButton(new_screen.ui, new_screen.on_back_button_clicked).show()
            else:
                BackButton(new_screen.ui, lambda: (UiUtil.change_screen(new_screen.previous_screen))).show()
        if isinstance(new_screen, MapScreen):
            new_screen.setup_locations()
            if new_screen.header_name and new_screen.is_disappearing_header and new_screen.is_transparent_header:
                new_screen.flash_map_header()

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