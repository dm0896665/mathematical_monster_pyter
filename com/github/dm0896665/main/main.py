import sys

from PySide6.QtWidgets import QApplication

from ui.main_menu import MainMenu

app = QApplication(sys.argv)

window = MainMenu()
window.setWindowTitle("Mathematical Monster Pyter")

window.show()
app.exec()