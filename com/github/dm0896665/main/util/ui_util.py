from PySide6 import QtCore, QtUiTools
import sys

class UiUtil:
    @staticmethod
    def load_ui_widget(ui_filename, parent=None):
        if not sys.path[0].endswith('ui'):
            ui_filename = "com/github/dm0896665/main/ui/" + ui_filename
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(ui_file, parent)
        ui_file.close()
        return ui