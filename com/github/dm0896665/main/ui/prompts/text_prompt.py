from PySide6.QtWidgets import QLineEdit

from com.github.dm0896665.main.ui.prompt import Prompt
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOptionButton, PromptOption


class TextPrompt(Prompt[str]):
    def __init__(self, prompt_text: str, *button_options: PromptOption):
        self.player_entry :QLineEdit = QLineEdit()
        self.player_entry.setStyleSheet("background-color: darkGray;")
        super().__init__(prompt_text, button_options)

    def add_options_to_prompt(self, button_options, option=None):
        self.prompt_options_container.addWidget(self.player_entry)
        okay_button: PromptOptionButton = PromptOptionButton(PromptOption.OKAY.get_option_text)
        okay_button.clicked.connect(lambda: self.on_prompt_button_clicked(self.player_entry.text()))
        okay_button.setStyleSheet("background-color: darkGray;")
        self.buttons.append(okay_button)
        self.prompt_options_container.addWidget(okay_button)

    def get_invalid_prompt_text(self, selected_option):
        return "Sorry, " + selected_option + " is invalid. Try again."

    def on_prompt_did_show(self):
        self.player_entry.setFocus()