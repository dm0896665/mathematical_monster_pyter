from PySide6.QtWidgets import QPushButton
import sys

from com.github.dm0896665.main.ui.screen import Screen
from com.github.dm0896665.main.ui.screens.new_game import NewGame
from com.github.dm0896665.main.util.ui_util import UiUtil


class MainMenu(Screen):
    def __init__(self):
        super().__init__('main_menu')
        self.exit_game_button: QPushButton = None
        self.load_game_button: QPushButton = None
        self.new_game_button: QPushButton = None

    def on_screen_will_show(self):
        self.new_game_button: QPushButton = self.findChild(QPushButton, "ui_new_game_button")
        self.load_game_button: QPushButton = self.findChild(QPushButton, "ui_load_game_button")
        self.exit_game_button: QPushButton = self.findChild(QPushButton, "ui_exit_game_button")
        self.initialize_button_listeners()

    def initialize_button_listeners(self):
        self.new_game_button.clicked.connect(self.new_game_button_clicked)
        self.load_game_button.clicked.connect(self.load_game_button_clicked)
        self.exit_game_button.clicked.connect(self.exit_game_button_clicked)

    def new_game_button_clicked(self):
        UiUtil.change_screen(NewGame())

    def load_game_button_clicked(self):
        print("You pressed button 2!")

    def exit_game_button_clicked(self):
        sys.exit(0)