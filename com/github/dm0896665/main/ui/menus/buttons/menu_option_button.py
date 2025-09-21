from enum import Enum
from PySide6.QtWidgets import QPushButton


class MenuOptionButton(QPushButton):
    def __init__(self, button_text):
        super().__init__(button_text)
        self.setMinimumHeight(30)

class MenuOption(Enum):
    FAST_ATTACK = "Fast attacks"
    LARGE_ATTACK = "Large attack"
    RUN = "Run"
    SWITCH_WEAPONS = "Switch weapons"
    VIEW_STATS = "View stats"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, option_text: str):
        self.option_text = option_text

    @property
    def get_option_text(self):
        return self.option_text