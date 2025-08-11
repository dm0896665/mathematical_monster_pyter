from enum import Enum
from PySide6.QtWidgets import QPushButton


class PromptOptionButton(QPushButton):
    def __init__(self, button_text):
        super().__init__(button_text)

class PromptOption(Enum):
    YES = "Yes"
    NO = "No"
    OKAY = "Okay"
    CANCEL = "Cancel"
    ON = "On"
    OFF = "Off"
    HEALTH = "Health"
    STRENGTH = "Strength"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, option_text: str):
        self.option_text = option_text

    @property
    def get_option_text(self):
        return self.option_text