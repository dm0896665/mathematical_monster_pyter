from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.core.weapon.weapon import Weapon
from com.github.dm0896665.main.core.weapon.weapon_util import WeaponUtil
from com.github.dm0896665.main.util.player_util import PlayerUtil
from com.github.dm0896665.main.util.ui_objects import Screen, ItemTableView, OutlinedLabel, \
    WeaponItemTableCell, WeaponItemTableCellType


class Blacksmith(Screen):
    def __init__(self):
        super().__init__()
        self.player: Player = None
        self.blacksmith_layout_widget: QWidget = None
        self.for_sale: ItemTableView = None
        self.inventory: ItemTableView = None
        self.has_back_button: bool = True

    def on_screen_did_show(self):
        # for_sale: ItemTableView = ItemTableView(5)
        # for weapon in WeaponUtil.get_all_weapons():
        #     cell: ItemTableCell = ItemTableCell(weapon.weapon_name, ImageUtil.load_image("weapons/" + weapon.weapon_image_name + ".png"), 80)
        #     for_sale.add_item(cell)
        #
        # inventory: ItemTableView = ItemTableView(5)
        # for weapon in WeaponUtil.get_owned_weapons():
        #     cell: ItemTableCell = ItemTableCell(weapon.weapon_name,
        #                                         ImageUtil.load_image("weapons/" + weapon.weapon_image_name + ".png"), 90)
        #     inventory.add_item(cell)
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

        self.adjust_layout_size()

    def on_buy_actioned_callback(self, weapon_cell: WeaponItemTableCell, did_buy: bool):
        if did_buy:
            cell: WeaponItemTableCell = WeaponItemTableCell(weapon_cell.weapon, self.player, WeaponItemTableCellType.SELL, self.on_sell_actioned_callback)
            self.inventory.add_item(cell)
            WeaponUtil.add_weapon(weapon_cell.weapon)

    def on_sell_actioned_callback(self, weapon_cell: WeaponItemTableCell, did_sell: bool):
        if did_sell:
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
