from PySide6 import QtCore, QtUiTools
import sys

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow

from com.github.dm0896665.main.ui.screen import Screen


class UiUtil:
    app: QApplication = QApplication(sys.argv)
    window: QMainWindow = QMainWindow()
    current_screen: Screen = None
    old_screen: Screen = None

    def __init__(self):
        UiUtil.window.setWindowTitle("Mathematical Monster Pyter")
        UiUtil.window.setMinimumSize(700, 500)

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
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_file_name + '.ui')
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file, parent)
        ui_file.close()
        return ui

    @staticmethod
    def change_screen(new_screen: Screen):
        UiUtil.old_screen: Screen = UiUtil.current_screen
        UiUtil.current_screen = new_screen

        if UiUtil.old_screen is not None:
            UiUtil.old_screen.on_screen_will_hide()
        UiUtil.load_ui_screen(new_screen.screen_name, new_screen)
        new_screen.on_screen_will_show()

        UiUtil.window.setCentralWidget(new_screen)

        if UiUtil.old_screen is not None:
            UiUtil.old_screen.on_screen_did_hide()
        new_screen.on_screen_did_show()