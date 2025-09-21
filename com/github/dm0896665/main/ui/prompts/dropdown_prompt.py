from PySide6.QtWidgets import QComboBox

from com.github.dm0896665.main.ui.prompt import Prompt
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOptionButton, PromptOption


class DropdownPrompt(Prompt[str]):
    def __init__(self, prompt_text: str, *dropdown_options: str):
        self.dropdown :QComboBox = QComboBox()
        self.dropdown.addItems(dropdown_options)
        self.dropdown.setStyleSheet("background-color: darkGray;")
        super().__init__(prompt_text, [])

    def add_options_to_prompt(self, dropdown_options, option=None):
        self.prompt_options_container.addWidget(self.dropdown)
        okay_button: PromptOptionButton = PromptOptionButton(PromptOption.OKAY.get_option_text)
        okay_button.clicked.connect(lambda: self.on_prompt_button_clicked(self.dropdown.currentText()))
        okay_button.setStyleSheet("background-color: darkGray;")
        self.buttons.append(okay_button)
        self.prompt_options_container.addWidget(okay_button)