import sys
import time

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSplitter, QSpacerItem, QSizePolicy

from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption, PromptOptionButton
from com.github.dm0896665.main.util.ui_util import UiUtil


class Prompt(QWidget):
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
        self.old_screen: QWidget = UiUtil.current_screen.ui
        self.old_screen.setEnabled(False)

        # Cover only 1/4 of the screen with the prompt and make sure the original screen's height is not altered
        self.setFixedHeight(UiUtil.window.height() / 4)
        self.old_screen.setFixedHeight(UiUtil.window.height())

        # Add splitter to help put prompt on bottom quarter of screen
        splitter: QSplitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.old_screen)
        splitter.addWidget(self)

        # Remove handler in the middle of splitter as the size ratio shouldn't change
        splitter.setHandleWidth(0)
        splitter.handle(1).setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        splitter.handle(1).setEnabled(False)

        # Add new split screen to window
        UiUtil.window.setCentralWidget(splitter)

        # Make sure prompt is on top, and that the main screen keeps its height
        self.raise_()
        splitter.installEventFilter(self)

    # This method will automatically be picked up by installEventFilter(self)
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.old_screen.setFixedHeight(event.size().height())
        return QWidget.eventFilter(self, source, event)


    def wait_for_results(self):
        while self.outcome is None:
            # If the user tried to close the window while waiting for a prompt, exit the program
            if not UiUtil.window.isVisible():
                print("The user has closed the window. Exiting")
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
        self.old_screen.setEnabled(True)
        UiUtil.window.setCentralWidget(UiUtil.current_screen.ui)

    def on_prompt_button_clicked(self, selected_option: PromptOption):
        self.outcome = selected_option