from typing import List

from com.github.dm0896665.main.core.math.math import Math
from com.github.dm0896665.main.core.weapon.weapon import Weapon


class Player:
    def __init__(self, name: str = "UNKNOWN"):
        self.upgrades = 0
        self.upgrade_limit = 11
        self.money = 1000
        self.health = 1000
        self.strength = 0
        self.bank = 0
        self.score = 0
        self.selected_weapon: Weapon = Weapon.STICK
        self.weapons: List[Weapon] = []
        self.math = Math()
        self.kills = 0
        self.deaths = 0
        self.saved = False
        self.level = 1
        self.name = name

    def get_kd(self):
        # initialize variables
        kd_formatted = None;
        kd = 0;

        # if the number deaths or kills are zero make the KD the number of kills
        if self.deaths == 0 or self.kills == 0:
            kd_formatted = f"{self.kills:.2f}"

        # otherwise, calculate the kill to death ratio
        else:
            kd = self.kills / self.deaths

        # if the KD is not 0 format the KD
        if kd != 0:
            kd_formatted = f"{kd:.2f}"

        # return the formatted KD
        return kd_formatted
