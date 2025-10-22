from com.github.dm0896665.main.util.ui_objects import MapScreen, MapLocation, UiObjects
from com.github.dm0896665.main.util.ui_util import UiUtil


class Village(MapScreen):
    def on_screen_did_show(self):
        back_image = UiUtil.load_image_map(self.get_map_location_image_path("back.png"))
        back_button: MapLocation = MapLocation(back_image, "Back", 10, 10, 0, 0, self.on_back_button_clicked, True)
        self.add_location(back_button)

        bank_image = UiUtil.load_image_map(self.get_map_location_image_path("bank.png"))
        bank_location: MapLocation = MapLocation(bank_image, "Bank", 30, 43, 4, 32, self.on_bank_location_clicked)
        self.add_location(bank_location)

        shop_image = UiUtil.load_image_map(self.get_map_location_image_path("shop.png"))
        shop_location: MapLocation = MapLocation(shop_image, "Shop", 24, 40, 39, 28, self.on_shop_location_clicked)
        self.add_location(shop_location)

        blacksmith_image = UiUtil.load_image_map(self.get_map_location_image_path("blacksmith.png"))
        blacksmith_location: MapLocation = MapLocation(blacksmith_image, "Blacksmith", 30, 35, 70, 36, self.on_blacksmith_location_clicked)
        self.add_location(blacksmith_location)

    def on_back_button_clicked(self, location: MapLocation):
        UiUtil.change_screen(self.previous_screen)

    def on_bank_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")

    def on_shop_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")

    def on_blacksmith_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")