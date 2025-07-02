from PySide6.QtWidgets import QWidget, QPushButton
from .ui_loader import UiLoader
import sys

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        UiLoader.load_ui_widget('main_menu.ui', self)
        self.new_game_button = self.findChild(QPushButton, "ui_new_game_button")
        self.load_game_button = self.findChild(QPushButton, "ui_load_game_button")
        self.exit_game_button = self.findChild(QPushButton, "ui_exit_game_button")
        self.initialize_button_listeners()

    def initialize_button_listeners(self):
        self.new_game_button.clicked.connect(self.new_game_button_clicked)
        self.load_game_button.clicked.connect(self.load_game_button_clicked)
        self.exit_game_button.clicked.connect(self.exit_game_button_clicked)

    def new_game_button_clicked(self):
        print("You pressed button 1!")

    def load_game_button_clicked(self):
        print("You pressed button 2!")

    def exit_game_button_clicked(self):
        sys.exit(0)