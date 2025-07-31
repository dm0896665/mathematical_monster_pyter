from PySide6.QtWidgets import QPushButton
import sys

from com.github.dm0896665.main.ui.screen import Screen


class MainMenu(Screen):
    def __init__(self):
        super().__init__('main_menu')
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