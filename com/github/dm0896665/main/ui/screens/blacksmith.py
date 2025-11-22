from PySide6.QtGui import QResizeEvent, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.core.weapon.weapon_util import WeaponUtil
from com.github.dm0896665.main.util.player_util import PlayerUtil
from com.github.dm0896665.main.util.ui_objects import Screen, ItemTableView, OutlinedLabel, \
    WeaponItemTableCell, WeaponItemTableCellType, PlayerStatusWidget


class Blacksmith(Screen):
    def __init__(self):
        super().__init__()
        self.player: Player = None
        self.blacksmith_layout_widget: QWidget = None
        self.for_sale: ItemTableView = None
        self.inventory: ItemTableView = None
        self.has_back_button: bool = True

    def on_screen_did_show(self):
        self.player: Player = PlayerUtil.current_player

        self.for_sale: ItemTableView = ItemTableView()
        for weapon in WeaponUtil.get_all_weapons():
            cell: WeaponItemTableCell = WeaponItemTableCell(weapon, self.player, WeaponItemTableCellType.BUY, self.on_buy_actioned_callback)
            self.for_sale.add_item(cell)

        self.inventory: ItemTableView = ItemTableView()
        for weapon in WeaponUtil.get_owned_weapons():
            cell: WeaponItemTableCell = WeaponItemTableCell(weapon, self.player, WeaponItemTableCellType.SELL, self.on_sell_actioned_callback)
            self.inventory.add_item(cell)

        self.blacksmith_layout_widget: QWidget = self.ui.blacksmith_layout

        for_sale_widget: QWidget = QWidget()
        for_sale_layout: QVBoxLayout = QVBoxLayout(for_sale_widget)
        for_sale_layout.addWidget(OutlinedLabel("Blacksmith", 40))
        for_sale_layout.addWidget(self.for_sale)
        self.blacksmith_layout_widget.layout().addWidget(for_sale_widget)

        inventory_widget: QWidget = QWidget()
        inventory_layout: QVBoxLayout = QVBoxLayout(inventory_widget)
        inventory_layout.addWidget(OutlinedLabel("Weapons to Sell", 40))
        inventory_layout.addWidget(self.inventory)
        self.blacksmith_layout_widget.layout().addWidget(inventory_widget)
        PlayerStatusWidget(self.player, self.ui).show()

        self.adjust_layout_size()

    def on_buy_actioned_callback(self, weapon_cell: WeaponItemTableCell):
        cell: WeaponItemTableCell = WeaponItemTableCell(weapon_cell.weapon, self.player, WeaponItemTableCellType.SELL, self.on_sell_actioned_callback)
        self.inventory.add_item(cell)
        self.inventory.resize_item_image()
        WeaponUtil.add_weapon(weapon_cell.weapon)

    def on_sell_actioned_callback(self, weapon_cell: WeaponItemTableCell):
        self.inventory.remove_item(weapon_cell)
        WeaponUtil.remove_weapon(weapon_cell.weapon)

    def resize_function(self, source: QWidget, event: QResizeEvent):
        self.adjust_layout_size()

    def adjust_layout_size(self):
        # Calculate the new layout size
        self.blacksmith_layout_widget.setFixedWidth(self.ui.width() * 7 / 8)
        self.blacksmith_layout_widget.setFixedHeight(self.ui.height() * 7 / 8)

        self.for_sale.setMaximumWidth(self.blacksmith_layout_widget.width() / 2)
        self.inventory.setMaximumWidth(self.blacksmith_layout_widget.width() / 2)
        self.ui.layout().setAlignment(Qt.AlignmentFlag.AlignBottom)
