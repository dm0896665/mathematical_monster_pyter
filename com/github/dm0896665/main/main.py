import sys

from PySide6.QtWidgets import QApplication
from com.github.dm0896665.main.ui.screen.main_menu import MainMenu

app = QApplication(sys.argv)
window = MainMenu()
window.setWindowTitle("Mathematical Monster Pyter")

window.show()
app.exec()