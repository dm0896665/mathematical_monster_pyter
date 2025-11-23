from typing import List, Any

from PySide6.QtCore import QObject, Signal, SignalInstance, Property

from com.github.dm0896665.main.core.math.math import Math
from com.github.dm0896665.main.core.weapon.weapon import Weapon


class PlayerSignal(QObject):
    player_property_changed = Signal(str, Any)

class Player:
    def __init__(self, name: str = "UNKNOWN"):
        self.upgrades: int = 0
        self.upgrade_limit: int = 11
        self._money: int = 1000
        self._health: int = 1000
        self._strength: int = 0
        self.bank: int = 0
        self.score: int = 0
        self._selected_weapon: Weapon = Weapon.STICK
        self.weapons: List[Weapon] = []
        self.math: Math = Math()
        self.kills: int = 0
        self.deaths: int = 0
        self.saved: bool = False
        self._level: int = 1
        self._name: str = name
        self.signal: PlayerSignal = PlayerSignal()
        self.property_change_listener: SignalInstance = self.signal.player_property_changed

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, health: int) -> None:
        self._health = health

    @property
    def strength(self) -> int:
        return self._strength

    @strength.setter
    def strength(self, strength: int) -> None:
        self._strength = strength

    @property
    def money(self) -> int:
        return self._money

    @money.setter
    def money(self, money: int) -> None:
        self._money = money

    @property
    def selected_weapon(self) -> Weapon:
        return self._selected_weapon

    @selected_weapon.setter
    def selected_weapon(self, weapon: Weapon) -> None:
        self._selected_weapon = weapon

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        self._level = level

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

    def __setattr__(self, name, value):
        # Detect property value changes
        if hasattr(self, name) and getattr(self, name) != value:
            super().__setattr__(name, value) # Make sure value is updated before emitting that there was a change
            self.property_change_listener.emit(name, value)
        super().__setattr__(name, value)
