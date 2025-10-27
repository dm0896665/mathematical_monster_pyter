from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent, QIntValidator
from PySide6.QtWidgets import QWidget

from com.github.dm0896665.main.util.custom_ui_widgets import Label, Button, IntegerInput
from com.github.dm0896665.main.util.player_util import PlayerUtil
from com.github.dm0896665.main.util.ui_objects import Screen
from com.github.dm0896665.main.util.ui_util import UiUtil


class BankMode(Enum):
    HOME = "home"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

class Bank(Screen):
    def __init__(self):
        super().__init__()
        self.bank_mode = BankMode.HOME

        self.action_button_layout: QWidget = None
        self.action_button: Button = None
        self.cancel_button: Button = None

        self.action_widget: QWidget = None
        self.action_amount: IntegerInput = None
        self.action_label: Label = None

        self.bank_layout_widget: QWidget = None
        self.current_coins_on_player: Label = None
        self.current_coins_in_bank: Label = None

        self.nav_button_layout: QWidget = None
        self.deposit_button: Button = None
        self.withdraw_button: Button = None
        self.back_button: Button = None

        self.player = PlayerUtil.current_player

    def on_screen_did_show(self):
        self.bank_layout_widget: Label = self.ui.bank_layout
        self.adjust_layout_size()

        self.current_coins_in_bank: Label = self.ui.current_coins_in_bank_label
        self.current_coins_in_bank.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_coins_on_player: Label = self.ui.current_coins_on_player_label
        self.current_coins_on_player.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_amounts()

        self.action_widget: QWidget = self.ui.action_widget
        self.action_widget.setVisible(False)
        self.action_widget.setStyleSheet("background-color: transparent;")

        self.action_amount: IntegerInput = self.ui.action_amount_input
        self.action_amount.setValidator(QIntValidator(0, 1000000))
        self.action_amount.textChanged.connect(self.on_action_amount_changed)
        self.action_amount.returnPressed.connect(self.action_button_clicked)

        self.action_label: Label = self.ui.action_label

        self.action_button_layout: QWidget = self.ui.action_button_layout
        self.action_button_layout.setVisible(False)
        self.action_button_layout.setStyleSheet("background-color: transparent;")
        self.action_button: Button = self.ui.action_button
        self.cancel_button: Button = self.ui.cancel_button

        self.nav_button_layout = self.ui.nav_button_layout
        self.nav_button_layout.setStyleSheet("background-color: transparent;")
        self.deposit_button: Button = self.ui.deposit
        self.withdraw_button: Button = self.ui.withdraw
        self.back_button: Button = self.ui.back

        self.initialize_button_listeners()

    def resize_function(self, source, event: QResizeEvent):
        self.adjust_layout_size()

    def adjust_layout_size(self):
        # Calculate the new layout size
        self.bank_layout_widget.setFixedWidth(self.ui.width() / 2)
        self.bank_layout_widget.setFixedHeight(self.ui.height() * 3 / 4)

    def initialize_button_listeners(self):
        self.action_button.clicked.connect(self.action_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

        self.deposit_button.clicked.connect(self.deposit_button_clicked)
        self.withdraw_button.clicked.connect(self.withdraw_button_clicked)
        self.back_button.clicked.connect(self.back_button_button_clicked)

    def action_button_clicked(self):
        if self.bank_mode == BankMode.DEPOSIT:
            self.player.bank = self.player.bank + int(self.action_amount.text())
            self.player.money = self.player.money - int(self.action_amount.text())
        else:
            self.player.bank = self.player.bank - int(self.action_amount.text())
            self.player.money = self.player.money + int(self.action_amount.text())

        self.update_amounts()
        self.bank_mode = BankMode.HOME
        self.update_layout_visibilities()

    def update_amounts(self):
        self.current_coins_in_bank.setText(str(self.player.bank) + " coins")
        self.current_coins_on_player.setText(str(self.player.money) + " coins")

    def cancel_button_clicked(self):
        self.bank_mode = BankMode.HOME
        self.update_layout_visibilities()

    def deposit_button_clicked(self):
        self.bank_mode = BankMode.DEPOSIT
        self.update_layout_visibilities()

    def withdraw_button_clicked(self):
        self.bank_mode = BankMode.WITHDRAW
        self.update_layout_visibilities()

    def on_action_amount_changed(self):
        if self.action_amount.text() == "":
            self.action_button.setDisabled(True)
            return

        amount: int = int(self.action_amount.text())

        if amount < 0:
            self.action_amount.setText("0")
            return

        if self.bank_mode == BankMode.DEPOSIT and amount > self.player.money:
            self.action_amount.setText(str(self.player.money))
        elif self.bank_mode == BankMode.WITHDRAW and amount > self.player.bank:
            self.action_amount.setText(str(self.player.bank))

        self.action_button.setDisabled(False)

    def update_layout_visibilities(self):
        self.action_button_layout.setVisible(self.bank_mode != BankMode.HOME)
        self.action_widget.setVisible(self.bank_mode != BankMode.HOME)
        self.nav_button_layout.setVisible(self.bank_mode == BankMode.HOME)

        if self.bank_mode != BankMode.HOME:
            self.action_amount.setFocus()
            self.action_button.setDisabled(True)
        else:
            self.action_amount.setText("")

        if self.bank_mode == BankMode.DEPOSIT:
            self.action_button.setText("Deposit")
            self.action_label.setText("Amount of coins to deposit:")
        else:
            self.action_button.setText("Withdraw")
            self.action_label.setText("Amount of coins to withdraw:")

    def back_button_button_clicked(self):
        UiUtil.change_screen(self.previous_screen)