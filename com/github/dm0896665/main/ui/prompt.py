import sys
import time
from typing import Generic, TypeVar, Callable

from PySide6 import QtCore
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSplitter, QSpacerItem, QSizePolicy

from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption, PromptOptionButton
from com.github.dm0896665.main.util.ui_util import UiUtil

T = TypeVar('T')


class Prompt(QWidget, Generic[T]):
    def __init__(self, prompt_text: str, *button_options: PromptOption):
        super().__init__()
        # initialize variables for later
        self.old_screen: QWidget = None
        self.outcome: T = None
        self.valid_check_function: Callable[[T], bool] = None
        self.get_custom_invalid_prompt_text: Callable[[T], bool] = None
        self.buttons = []
        self.loop: QtCore.QEventLoop = QtCore.QEventLoop(self)

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
        self.add_options_to_prompt(button_options)

        # Create a container for the entire prompt
        self.prompt_container: QVBoxLayout = QVBoxLayout()
        self.prompt_container.addWidget(self.prompt_label)
        self.prompt_container.addLayout(self.prompt_options_container)

        # Set the layout of the Prompt
        self.setLayout(self.prompt_container)

    def add_options_to_prompt(self, button_options):
        for option in button_options:
            option_button: PromptOptionButton = PromptOptionButton(option.get_option_text)
            option_button.clicked.connect(lambda state, o=option: self.on_prompt_button_clicked(o))
            self.buttons.append(option_button)
            self.prompt_options_container.addWidget(option_button)

    def show_and_get_results(self, prompt=None) -> T:
        if prompt is None:
            prompt = self
        self.show_prompt(prompt)
        self.wait_for_results()
        self.hide_prompt()
        return self.outcome

    def show_prompt(self, prompt=None):
        if prompt is None:
            prompt = self

        # Keep current screen to replace back later
        self.old_screen: QWidget = UiUtil.current_screen.ui
        self.old_screen.setEnabled(False)

        # Cover only 1/4 of the screen with the prompt and make sure the original screen's height is not altered
        self.setFixedHeight(UiUtil.window.height() / 4)
        self.old_screen.setFixedHeight(UiUtil.window.height())

        # Add splitter to help put prompt on bottom quarter of screen
        splitter: QSplitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.old_screen)
        splitter.addWidget(prompt)

        # Remove handler in the middle of splitter as the size ratio shouldn't change
        splitter.setHandleWidth(0)
        splitter.handle(1).setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        splitter.handle(1).setEnabled(False)

        # Add new split screen to window
        UiUtil.window.setCentralWidget(splitter)
        self.raise_()
        splitter.installEventFilter(self) # This will pick up self.eventFilter
        self.setFocus()
        self.on_prompt_did_show()

    # This method will automatically be picked up by installEventFilter(self)
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.old_screen.setFixedHeight(event.size().height())
        return QWidget.eventFilter(self, source, event)

    # This method will automatically be picked up by the QT Framework
    def keyPressEvent(self, event):
        # Enter key is the first option
        if event.key() + 1 == Qt.Key_Enter or event.key() + 1 == Qt.Key_Insert:
            self.buttons[0].click()
            return

        # Convert to Function key index
        key = event.key() - 16777264

        # Make sure it's an available Function key and "click" it
        if 0 <= key < len(self.buttons):
            self.buttons[key].click()

    def wait_for_results(self):
        self.loop.exec_()

    def hide_prompt(self):
        # Reset back to base screen and re-enable it (No prompt)
        self.old_screen.setEnabled(True)
        UiUtil.window.setCentralWidget(UiUtil.current_screen.ui)

    def close(self):
        self.loop.quit()

    def on_prompt_button_clicked(self, selected_option: T):
        if not self.is_entry_valid(selected_option):
            self.hide_prompt()
            Prompt(self.get_custom_invalid_prompt_text(selected_option), PromptOption.OKAY).show_and_get_results()
            self.show_prompt()
            return

        self.outcome = selected_option
        self.loop.exit(True)

    def is_entry_valid(self, selected_option: T) -> bool:
        if self.valid_check_function is None:
            return True
        else:
            return self.valid_check_function(selected_option)

    def get_invalid_prompt_text(self, selected_option: T) -> str:
        if self.get_custom_invalid_prompt_text is None:
            return "Sorry, that input is invalid. Try again."
        else:
            return self.get_custom_invalid_prompt_text(selected_option)

    def on_prompt_did_show(self):
        pass