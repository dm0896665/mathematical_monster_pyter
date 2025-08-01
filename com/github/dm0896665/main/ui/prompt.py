import sys
import time

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSplitter, QSpacerItem, QSizePolicy

from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption, PromptOptionButton
from com.github.dm0896665.main.util.ui_util import UiUtil


class Prompt(QGroupBox):
    def __init__(self, prompt_text: str, *button_options: PromptOption):
        super().__init__()
        # initialize variables for later
        self.old_screen: QWidget = None
        self.outcome: PromptOption = None

        # Create prompt label
        self.prompt_label: QLabel = QLabel()
        self.prompt_label.setText(prompt_text)
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing)

        # Create container for prompt options
        self.prompt_options_container:QHBoxLayout = QHBoxLayout()

        # Add an expanding spacer to keep prompt options on the right side
        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.prompt_options_container.addItem(horizontal_spacer)

        # Create option buttons and apply an event handler to each to record the results later and add them to a container
        for option in button_options:
            option_button: PromptOptionButton = PromptOptionButton(option.get_option_text)
            option_button.clicked.connect(lambda state, o = option: self.on_prompt_button_clicked(o))
            self.prompt_options_container.addWidget(option_button)

        # Create a container for the entire prompt
        self.prompt_container: QVBoxLayout = QVBoxLayout()
        self.prompt_container.addWidget(self.prompt_label)
        self.prompt_container.addLayout(self.prompt_options_container)

        # Set the layout of the Prompt
        self.setLayout(self.prompt_container)

    def show_and_get_results(self):
        self.show_prompt()
        self.wait_for_results()
        self.hide_prompt()
        return self.outcome

    def show_prompt(self):
        # Keep current screen to replace back later
        UiUtil.current_screen.setEnabled(False)
        self.old_screen: QWidget = UiUtil.current_screen

        # Add splitter to cover only 1/4 of the screen with the prompt
        splitter: QSplitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.old_screen)
        self.setAlignment(Qt.AlignCenter)
        splitter.addWidget(self)
        splitter.setSizes([UiUtil.window.height() * 3 / 4, UiUtil.window.height() / 4])

        # Add new split screen to window
        UiUtil.window.setCentralWidget(splitter)

    def wait_for_results(self):
        while self.outcome is None:
            # If the user tried to close the window while waiting for a prompt, exit the program
            if not UiUtil.window.isVisible():
                sys.exit(0)

            # Keep waiting for user to select a prompt option
            UiUtil.app.processEvents()
            try:
                time.sleep(0.05)
            except KeyboardInterrupt:
                print("Prompt wait interrupted. Exiting")
                sys.exit(0)

    def hide_prompt(self):
        # Reset back to base screen and re-enable it (No prompt)
        UiUtil.window.setCentralWidget(self.old_screen)
        UiUtil.current_screen.setEnabled(True)

    def on_prompt_button_clicked(self, selected_option: PromptOption):
        self.outcome = selected_option