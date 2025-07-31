from PySide6 import QtCore, QtUiTools
import sys

from PySide6.QtWidgets import QApplication, QWidget


class UiUtil:
    app: QApplication = QApplication(sys.argv)
    window: QWidget = QWidget()

    def __init__(self):
        UiUtil.window.setWindowTitle("Mathematical Monster Pyter")

    @staticmethod
    def load_ui_screen(ui_screen_name, parent=None):
        return UiUtil.load_ui_widget('screens/' + ui_screen_name, parent)

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
    def change_screen(new_screen):
        UiUtil.window = new_screen
        UiUtil.window.show()