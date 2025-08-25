import re

from PySide6.QtWidgets import QWidget


class Screen(QWidget):
    def __init__(self, screen_name: str = None):
        super().__init__()
        if screen_name is None:
            screen_name = self.camel_to_snake(self.__class__.__name__)
        self.screen_name = screen_name

        self.ui :QWidget = None

    def camel_to_snake(self, name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def on_screen_will_show(self):
        pass

    def on_screen_did_show(self):
        pass

    def on_screen_will_hide(self):
        pass

    def on_screen_did_hide(self):
        pass
