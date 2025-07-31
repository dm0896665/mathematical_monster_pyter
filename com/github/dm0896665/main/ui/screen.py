from PySide6.QtWidgets import QWidget

from com.github.dm0896665.main.util.ui_util import UiUtil

class Screen(QWidget):
    def __init__(self, screen_name):
        super().__init__()
        UiUtil.load_ui_screen(screen_name, self)
