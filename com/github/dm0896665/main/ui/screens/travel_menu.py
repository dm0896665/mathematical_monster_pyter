from PySide6.QtCore import Qt

from com.github.dm0896665.main.ui.prompts.okay_prompt import OkayPrompt
from com.github.dm0896665.main.util.ui_objects import MapScreen, MapLocation
from com.github.dm0896665.main.util.ui_util import UiUtil


class TravelMenu(MapScreen):
    def __init__(self, is_first_time: bool = False):
        super().__init__()
        self.is_first_time: bool = is_first_time


    def on_screen_did_show(self):
        bank_image = UiUtil.load_image_map(self.get_screen_image_path("bank.png"))
        bank_location: MapLocation = MapLocation(bank_image, "Bank", 20, 20, 7, 25, self.on_bank_location_clicked)
        self.add_location(bank_location)

        village_image = UiUtil.load_image_map(self.get_screen_image_path("village.png"))
        village_location: MapLocation = MapLocation(village_image, "Village", 40, 30, 38, 34, self.on_village_location_clicked)
        self.add_location(village_location)

        forrest_image = UiUtil.load_image_map(self.get_screen_image_path("forrest.png"))
        forrest_location: MapLocation = MapLocation(forrest_image, "Forrest", 40, 40, 62, 62, self.on_forrest_location_clicked)
        self.add_location(forrest_location)

        if self.is_first_time:
            OkayPrompt("Click a location on the map to go there.")

    def on_bank_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")

    def on_village_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")

    def on_forrest_location_clicked(self, location: MapLocation):
        print(f"{location.name} was clicked!")