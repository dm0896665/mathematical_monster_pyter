import random
from typing import List

from com.github.dm0896665.main.core.monster.monster import Monster
from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.core.weapon.weapon import Weapon
from com.github.dm0896665.main.ui.prompts.dropdown_prompt import DropdownPrompt
from com.github.dm0896665.main.util.player_util import PlayerUtil


class WeaponUtil:
    @staticmethod
    def switch_weapon():
        player: Player = PlayerUtil.current_player
        selected_weapon: Weapon = player.selected_weapon
        current_weapons: List[Weapon] = player.weapons + [selected_weapon]
        weapon_names: List[str] = [weapon.weapon_name for weapon in current_weapons]

        new_weapon: str = DropdownPrompt("You currently have the " + selected_weapon.weapon_name + " that does " + str(selected_weapon.damage) + " damage with an attack rate of " + str(selected_weapon.attack_rate) + " selected.\n What weapon would you like to swap it out for?",
                                         *weapon_names).show_and_get_results()

        if selected_weapon.weapon_name != new_weapon:
            player.weapons.append(selected_weapon)
            player.selected_weapon = next((weapon for weapon in current_weapons if weapon.weapon_name == new_weapon), None)

    @staticmethod
    def get_owned_weapons() -> List[Weapon]:
        player: Player = PlayerUtil.current_player
        return player.weapons + [player.selected_weapon]

    @staticmethod
    def get_unowned_weapons() -> List[Weapon]:
        owned_weapons: List[Weapon] = WeaponUtil.get_owned_weapons()
        owned_weapon_names: List[str] = [weapon.name for weapon in owned_weapons]
        return [weapon for weapon in Weapon if weapon.name not in owned_weapon_names]

    @staticmethod
    def get_all_weapons() -> List[Weapon]:
        return [weapon for weapon in Weapon]

    @staticmethod
    def weapon_drop(monster: Monster) -> List[Weapon]:
        # Initialize variables
        weapons_dropped: List[Weapon] = []
        owned_weapons: List[Weapon] = WeaponUtil.get_owned_weapons()
        unowned_weapons: List[Weapon] = WeaponUtil.get_unowned_weapons()
        owned_weapon_drop_chance: int = 50
        unowned_weapon_drop_chance: int = 50

        # Calculate owned and unowned weapon drop chance
        # Owned weapons will drop after player has more than 4 weapons
        # Unowned weapons will drop until the player only has 4 unowned weapons
        if len(owned_weapons) > 4:
            owned_weapon_drop_chance = random.randint(0,100)
        if len(unowned_weapons) > 4:
            unowned_weapon_drop_chance = random.randint(0,100)

        # Initialize owned weapon pool
        weapons_in_owned_pool: int = len(owned_weapons) / 4
        owned_weapon_pool_section: int = 0

        # Initialize unowned weapon pool
        weapons_in_unowned_pool: int = len(unowned_weapons) / 4
        unowned_weapon_pool_section: int = 0

        # Find weapon pool section based on monster health
        weapon_pool_section: int = 0
        if 1000 >= monster.get_original_health() >= 0:
            weapon_pool_section = 1
        elif 2500 >= monster.get_original_health() > 1000:
            weapon_pool_section = 2
        elif 4000 >= monster.get_original_health() > 2500:
            weapon_pool_section = 3
        elif monster.get_original_health() > 4000:
            weapon_pool_section = 4

        # Assign the section for owned weapons at a 25% chance and for unowned weapons at a 15% chance
        if 25 > owned_weapon_drop_chance >= 0:
            owned_weapon_pool_section = weapon_pool_section
        if 15 > unowned_weapon_drop_chance >= 0:
            unowned_weapon_pool_section = weapon_pool_section

        # Add copy of owned weapon to drop list if one was dropped
        if owned_weapon_pool_section > 0:
            owned_weapon_pool_max: int = (weapons_in_owned_pool * owned_weapon_pool_section) - 1
            owned_weapon_pool_min: int = owned_weapon_pool_max - weapons_in_owned_pool + 1
            found_index: int = random.randint(owned_weapon_pool_min, owned_weapon_pool_max)
            weapons_dropped.append(Weapon.get_weapon_by_weapon_name(owned_weapons[found_index].weapon_name))

        # Add unowned weapon to drop list if one was dropped
        if unowned_weapon_pool_section > 0:
            unowned_weapon_pool_max: int = (weapons_in_unowned_pool * unowned_weapon_pool_section) - 1
            unowned_weapon_pool_min: int = unowned_weapon_pool_max - weapons_in_unowned_pool + 1
            found_index: int = random.randint(unowned_weapon_pool_min, unowned_weapon_pool_max)
            weapons_dropped.append(unowned_weapons[found_index])

        # Return dropped weapons
        return weapons_dropped

    @staticmethod
    def remove_weapon(weapon: Weapon):
        player: Player = PlayerUtil.current_player
        if player.selected_weapon == weapon:
            player.selected_weapon = player.weapons[0]
            player.weapons.remove(player.selected_weapon)
        else:
            player.weapons.remove(weapon)

    @staticmethod
    def add_weapon(weapon: Weapon):
        player: Player = PlayerUtil.current_player
        player.weapons.append(player.selected_weapon)
        player.selected_weapon = weapon