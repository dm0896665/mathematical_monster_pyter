import math
from typing import Generic, TypeVar, Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption, PromptOptionButton
from com.github.dm0896665.main.util.thread_util import UiThreadUtil
from com.github.dm0896665.main.util.ui_objects import UiObjects
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
        self.prompt_container_Layout: QVBoxLayout = QVBoxLayout()
        self.prompt_container_Layout.addWidget(self.prompt_label)
        self.prompt_container_Layout.addLayout(self.prompt_options_container)

        # Set the layout of the Prompt
        self.prompt_container: QWidget = QWidget()
        self.prompt_container.setLayout(self.prompt_container_Layout)

        self.prompt_container.setParent(self)
        self.prompt_container.setStyleSheet("background-color: gray;")

    def add_options_to_prompt(self, button_options):
        for option in button_options:
            option_button: PromptOptionButton = PromptOptionButton(option.get_option_text)
            option_button.clicked.connect(lambda state, o=option: self.on_prompt_button_clicked(o))
            option_button.setStyleSheet("background-color: darkGray;")
            self.buttons.append(option_button)
            self.prompt_options_container.addWidget(option_button)

    def show_and_get_results(self) -> T:
        if UiThreadUtil.is_on_ui_thread():
            self.do_show_and_get_results()
        else:
            UiThreadUtil.run_on_ui_and_wait(self.do_show_and_get_results)
        return self.outcome

    def do_show_and_get_results(self):
        self.initialize_prompt()
        self.show_prompt()
        self.wait_for_results()
        self.hide_prompt()

    def initialize_prompt(self):
        self.old_screen: QWidget = UiObjects.current_screen.ui

        # Cover only 1/4 of the screen with the prompt
        self.prompt_container.setFixedHeight(UiObjects.window.height() / 4)

        # Make sure prompt fills the full screen
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet('''
                            QWidget#prompt {
                                background-color: rgba(64, 64, 64, .64);
                            }
                        ''')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.setObjectName("prompt")

        # This will pick up self.eventFilter
        self.old_screen.installEventFilter(self)

    def show_prompt(self):
        self.setParent(self.old_screen)
        self.resize_prompt()
        self.raise_()
        UiUtil.toggle_visibility(self, 100)
        self.setFocus()
        self.on_prompt_did_show()

    def resize_prompt(self):
        # Get the new central widget size
        parent_height = UiObjects.window.height()
        parent_width = UiObjects.window.width()

        # Set the height of the top widget to 50%
        self.prompt_container.setFixedHeight(math.ceil(parent_height / 4))
        self.prompt_container.setFixedWidth(parent_width)
        self.setFixedHeight(parent_height)
        self.setFixedWidth(parent_width)

        # Move to bottom of screen
        self.prompt_container.move(QPoint(0, int(parent_height * 3/4)))

    def showEvent(self, event):
        self.setGeometry(self.old_screen.rect())

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(source.rect())
            self.resize_prompt()
        return super().eventFilter(source, event)

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
        UiUtil.toggle_visibility(self, 100)
        self.setParent(None)

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