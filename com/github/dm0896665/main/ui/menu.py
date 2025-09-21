from typing import Generic, TypeVar, Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtWidgets import QWidget, QSpacerItem, QSizePolicy, QHBoxLayout, QGridLayout

from com.github.dm0896665.main.ui.menus.buttons.menu_option_button import MenuOptionButton, MenuOption
from com.github.dm0896665.main.util.ui_util import UiUtil

T = TypeVar('T')


class Menu(QWidget, Generic[T]):
    def __init__(self, column_number, *button_options: MenuOption):
        super().__init__()
        button_options = [MenuOption.FAST_ATTACK, MenuOption.LARGE_ATTACK, MenuOption.SWITCH_WEAPONS, MenuOption.RUN, MenuOption.VIEW_STATS]
        # initialize variables for later
        self.old_screen: QWidget = None
        self.outcome: T = None
        self.valid_check_function: Callable[[T], bool] = None
        self.get_custom_invalid_menu_text: Callable[[T], bool] = None
        self.buttons = []
        self.menu: Menu = None
        self.column_number: int = column_number
        self.loop: QtCore.QEventLoop = QtCore.QEventLoop(self)

        # Create container for menu options
        self.menu_options_container:QGridLayout = QGridLayout()

        # Create option buttons and apply an event handler to each to record the results later and add them to a container
        self.add_options_to_menu(button_options)

        # Create a container for the entire menu
        self.menu_container: QWidget = QWidget()
        self.menu_container.setLayout(self.menu_options_container)

        # Set the layout of the Menu
        self.menu_container.setParent(self)
        self.menu_container.setStyleSheet("background-color: gray;")

    def add_options_to_menu(self, button_options):
        # Set up variables for adding to menu
        button_count: int = len(button_options)
        last_row_index: int = button_count // self.column_number
        is_uneven: bool = not (button_count / self.column_number).is_integer()

        # Create container for buttons if it doesn't split evenly across the columns
        uneven_row_container: QHBoxLayout = QHBoxLayout()
        uneven_row_container.setContentsMargins(0, 0, 0, 0)

        # Initialize variables
        row_index: int = 0
        col_index: int = 0

        # Add buttons to menu
        for option in button_options:
            # Set up button
            option_button: MenuOptionButton = MenuOptionButton(option.get_option_text)
            option_button.clicked.connect(lambda state, o=option: self.on_menu_button_clicked(o))
            option_button.setStyleSheet("background-color: darkGray;")

            # Add button to list for key functions
            self.buttons.append(option_button)

            # Only add button to uneven row if it's an uneven number of buttons, and it's the last row
            if is_uneven and row_index == last_row_index:
                uneven_row_container.addWidget(option_button)
            else:
                # Otherwise, add button to the menu option container
                self.menu_options_container.addWidget(option_button, row_index, col_index, Qt.AlignVCenter)

                # Update column index
                col_index += 1

                # if it was the last column, reset column to 0 and go down a row
                if col_index == self.column_number:
                    col_index = 0
                    row_index += 1

        # If there was an uneven number of buttons for the number of columns, add the uneven row to the menu option container
        if is_uneven:
            w: QWidget = QWidget()
            w.setLayout(uneven_row_container)
            self.menu_options_container.addWidget(w, last_row_index, 0, 1, self.column_number, Qt.AlignVCenter)

    def show_and_get_results(self, menu=None) -> T:
        if menu is None:
            menu = self
        self.initialize_menu(menu)
        self.show_menu()
        self.wait_for_results()
        self.hide_menu()
        return self.outcome

    def initialize_menu(self, menu=None):
        # Initialize class variable
        self.old_screen: QWidget = UiUtil.current_screen.ui

        # Make menu background
        menu.setAutoFillBackground(True)
        menu.setAttribute(QtCore.Qt.WA_StyledBackground)
        menu.setStyleSheet('''
                    QWidget#menu {
                        background-color: rgba(64, 64, 64, .64);
                    }
                ''')
        menu.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)

        # Add layout to fill screen
        full_layout = QtWidgets.QVBoxLayout(menu)
        full_layout.addWidget(menu, alignment=QtCore.Qt.AlignCenter)

        # Add name for styling
        menu.setObjectName('menu')

        # Set up event handlers and add menu to old screen
        self.old_screen.installEventFilter(self)
        menu.setParent(self.old_screen)

    def resizeEvent(self, event):
        # Call the parent's resizeEvent first
        super().resizeEvent(event)

        # Get the new central widget size
        parent_height = UiUtil.window.height() if UiUtil.window.height() < 1400 else 1400
        parent_width = UiUtil.window.width() if UiUtil.window.width() < 1000 else 1000

        # Set the height of the top widget to 50%
        self.menu_container.setFixedHeight(int(parent_height / 2))
        self.menu_container.setFixedWidth(int(parent_width / 2))

        # Calculate the new center location
        target_rect = UiUtil.window.centralWidget().geometry()
        x = target_rect.x() + (target_rect.width() - self.menu_container.width()) / 2
        y = target_rect.y() + (target_rect.height() - self.menu_container.height()) / 2

        # Move menu to center
        self.menu_container.move(QPoint(int(x), int(y)))

    def show_menu(self):
        self.show()
        self.raise_()
        self.setFocus()
        self.on_menu_did_show()

    def close(self):
        self.loop.quit()

    def showEvent(self, event):
        self.setGeometry(self.old_screen.rect())

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(source.rect())
            self.old_screen.setGeometry(source.rect())
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

    def hide_menu(self):
        self.hide()
        self.setParent(None)
        self.loop.quit()

    def on_menu_button_clicked(self, selected_option: T):
        self.outcome = selected_option
        self.loop.exit(True)

    def on_menu_did_show(self):
        pass