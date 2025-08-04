from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy


class Screen(QWidget):
    def __init__(self, screen_name):
        super().__init__()
        self.screen_name = screen_name

        layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(layout)
        self.ui :QWidget = None

    def on_screen_will_show(self):
        pass

    def on_screen_did_show(self):
        pass

    def on_screen_will_hide(self):
        pass

    def on_screen_did_hide(self):
        pass
