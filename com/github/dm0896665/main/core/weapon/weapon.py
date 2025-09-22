from enum import Enum

class WeaponType(Enum):
    PICKAXE_AND_CLUB = "Pickaxe and Club", 4
    SWORD = "Sword", 5
    SPEAR = "Spear", 4
    KNIFE = "Knife", 7
    BOW = "Bow", 3
    UNKNOWN = "", 0
    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, weapon_type_name: str, attack_rate: int):
        self.weapon_type_name = weapon_type_name
        self.attack_rate = attack_rate

    def __str__(self):
        return self.weapon_type_name

    @staticmethod
    def get_weapon_type_by_weapon_type_name(weapon_type_name: str):
        for weapon_type in WeaponType:
            if weapon_type.weapon_type_name == weapon_type_name:
                return weapon_type
        return None

    def get_weapon_type_name(self):
        return self.weapon_type_name

    def get_attack_rate(self):
        return self.attack_rate

class Weapon(Enum):
    STICK = "Stick", 100, 0, 50, WeaponType.PICKAXE_AND_CLUB

    THROWING_KNIFE = "Throwing Knife", 163, 50, 100, WeaponType.KNIFE
    KNIFE = "Knife", 175, 100, 150, WeaponType.KNIFE
    CLEAVER = "Cleaver", 200, 150, 200, WeaponType.KNIFE

    SMALL_PICKAXE = "Small Pickaxe", 215, 150, 250, WeaponType.PICKAXE_AND_CLUB
    PICKAXE = "Pickaxe", 247, 200, 300, WeaponType.PICKAXE_AND_CLUB
    LARGE_PICKAXE = "Large Pickaxe", 260, 250, 340, WeaponType.PICKAXE_AND_CLUB

    SMALL_CLUB = "Small Club", 270, 250, 360, WeaponType.PICKAXE_AND_CLUB
    CLUB = "Club", 290, 300, 390, WeaponType.PICKAXE_AND_CLUB
    LARGE_CLUB = "Large Club", 350, 350, 410, WeaponType.PICKAXE_AND_CLUB

    DAGGER = "Dagger", 400, 350, 500, WeaponType.SWORD
    SWORD = "Sword", 435, 400, 550, WeaponType.SWORD
    LONGSWORD = "Longsword", 465, 450, 595, WeaponType.SWORD

    JAVELIN = "Javelin", 400, 350, 500, WeaponType.SPEAR
    SPEAR = "Spear", 435, 400, 550, WeaponType.SPEAR
    LONG_SPEAR = "Long Spear", 465, 450, 595, WeaponType.SPEAR

    SHORT_BOW = "Short Bow", 470, 450, 650, WeaponType.BOW
    BOW_AND_ARROW = "Bow and Arrow", 499, 500, 720, WeaponType.BOW
    LONG_BOW = "Long Bow", 530, 550, 780, WeaponType.BOW

    LIGHT_CROSSBOW = "Light Crossbow", 570, 550, 830, WeaponType.BOW
    CROSSBOW = "Crossbow", 600, 600, 890, WeaponType.BOW
    HEAVY_CROSSBOW = "Heavy Crossbow", 700, 650, 1000, WeaponType.BOW

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, weapon_name: str, damage: int, strength: int, price: int, weapon_type: WeaponType):
        self.weapon_name: str = weapon_name
        self.damage: int = damage
        self.strength: int = strength
        self.price: int = price
        self.weapon_type: WeaponType = weapon_type
        self.attack_rate: int = weapon_type.attack_rate

    def __str__(self):
        return (self.weapon_name + "- Damage: " + str(self.damage) + ", Attack Rate: " + str(self.weapon_type.attack_rate)
                + ", Strength Required: " + str(self.strength) + ", Weapon Type: " + str(self.weapon_type))

    @staticmethod
    def get_weapon_by_weapon_name(weapon_name: str):
        for weapon in Weapon:
            if weapon.weapon_name == weapon_name:
                return weapon
        return None
