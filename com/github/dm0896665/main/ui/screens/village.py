from com.github.dm0896665.main.ui.screens.bank import Bank
from com.github.dm0896665.main.ui.screens.blacksmith import Blacksmith
from com.github.dm0896665.main.util.image_util import ImageUtil
from com.github.dm0896665.main.util.ui_objects import MapScreen, MapLocation
from com.github.dm0896665.main.util.ui_util import UiUtil


class Village(MapScreen):
    def __init__(self):
        super().__init__("The Village")
        self.has_back_button = True

    def setup_locations(self):
        bank_image = ImageUtil.load_image_map(self.get_map_location_image_path("bank.png"))
        bank_location: MapLocation = MapLocation(bank_image, "Bank", 30, 43, 3, 30, self.on_bank_location_clicked)
        self.add_location(bank_location)

        shop_image = ImageUtil.load_image_map(self.get_map_location_image_path("shop.png"))
        shop_location: MapLocation = MapLocation(shop_image, "Shop", 24, 40, 39, 28, self.on_shop_location_clicked)
        self.add_location(shop_location)

        blacksmith_image = ImageUtil.load_image_map(self.get_map_location_image_path("blacksmith.png"))
        blacksmith_location: MapLocation = MapLocation(blacksmith_image, "Blacksmith", 33, 45, 67, 27, self.on_blacksmith_location_clicked)
        self.add_location(blacksmith_location)

    def on_bank_location_clicked(self, location: MapLocation):
        UiUtil.change_screen(Bank())

    def on_shop_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")

    def on_blacksmith_location_clicked(self, location: MapLocation):
        UiUtil.change_screen(Blacksmith())