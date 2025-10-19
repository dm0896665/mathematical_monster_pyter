import random
from enum import Enum

from com.github.dm0896665.main.util.player_util import PlayerUtil


class MonsterType(Enum):
    PRACTICE_DUMMY = "Dummy", 1000, 100, 1
    ZOMBIE = "Zombie", 1000, 200, 1
    VAMPIRE = "Vampire", 750, 180, 2
    SKELETON = "Skeleton", 1000, 200, 2
    WEREWOLF = "Werewolf", 1500, 200, 2
    BANSHEE = "Banshee", 2000, 100, 3
    CYCLOPS = "Cyclops", 3000, 500, 1
    CHUPACABRA = "Chupacabra", 500, 100, 5
    YETI = "Yeti", 2500, 350, 1
    MUMMY = "Mummy", 1000, 150, 1
    DEMON = "Demon", 1800, 250, 2
    FRANKENSTEIN = "Frankenstein", 1200, 220, 1
    GHOST = "Ghost", 1000, 50, 10
    SPIDER = "Spider", 900, 35, 25
    GHOUL = "Ghoul", 1100, 150, 3
    KRAKEN = "Kraken", 4500, 550, 1
    ORC = "Orc", 1300, 200, 2
    MINOTAUR = "Minotaur", 2200, 320, 2
    SIREN = "Siren", 1700, 200, 3
    CERBERUS = "Cerberus", 3000, 100, 3
    SERPENT = "Serpent", 2000, 300, 1
    DRAGON = "Dragon", 5000, 700, 1
    ELDRITCH_HORROR = "Eldritch Horror", 10000, 700, 3

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, monster_name: str, health: int, attack: int, attack_rate: int):
        self.monster_name = monster_name
        self.health = health
        self.attack = attack
        self.attack_rate = attack_rate

    def __str__(self):
        return self.monster_name

    @staticmethod
    def get_monster_type_by_monster_name(monster_name: str):
        for monster_type in MonsterType:
            if monster_type.monster_name == monster_name:
                return monster_type
        return None

    def get_monster_name(self):
        return self.monster_name

    def get_health(self):
        return self.health

    def get_attack(self):
        return self.attack

    def get_attack_rate(self):
        return self.attack_rate

    @staticmethod
    def get_random_monster_type(max_index: int = None):
        if max_index is None or max_index >= MonsterType.get_monster_count():
            max_index = MonsterType.get_monster_count() - 1

        random_index = random.randint(0, max_index)
        monsters = list(filter(lambda m: m.get_monster_name() != MonsterType.PRACTICE_DUMMY.get_monster_name(), [monster for monster in MonsterType]))
        return monsters[random_index]

    @staticmethod
    def get_monster_count():
        return len(MonsterType) - 1


class Monster:
    def __init__(self, monster_type: MonsterType = None):
        if monster_type is None:
            monster_type = Monster.get_random_monster_type()
        self.monster_type: MonsterType = monster_type
        self.monster_name: str = monster_type.get_monster_name()
        self.health: int = monster_type.get_health()
        self.attack: int = monster_type.get_attack()
        self.attack_rate: int = monster_type.get_attack_rate()

    def get_original_health(self):
        return self.monster_type.get_health()

    def get_original_attack(self):
        return self.monster_type.get_attack()

    @staticmethod
    def get_random_monster_type():
        level: int = PlayerUtil.current_player.level
        if level == 100:
            return MonsterType.get_random_monster_type()

        monsters_per_level_rank: float = MonsterType.get_monster_count() / 10

        level_rank: int = level / 10 + 1 # level rank starts at 1

        number_of_possible_monsters: int = round(level_rank * monsters_per_level_rank) + 1

        return MonsterType.get_random_monster_type(number_of_possible_monsters)
