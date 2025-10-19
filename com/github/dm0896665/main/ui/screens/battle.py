import copy
import random
import time
from enum import Enum
from typing import Callable

from PySide6.QtCore import QThreadPool, Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPalette, QResizeEvent, QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QGraphicsPixmapItem, \
    QSizePolicy

from com.github.dm0896665.main.core.monster.monster import Monster, MonsterType
from com.github.dm0896665.main.core.player import player
from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.core.weapon.weapon import Weapon
from com.github.dm0896665.main.core.weapon.weapon_util import WeaponUtil
from com.github.dm0896665.main.ui.menu import Menu
from com.github.dm0896665.main.ui.menus.buttons.menu_option_button import MenuOption
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption
from com.github.dm0896665.main.ui.prompts.okay_prompt import OkayPrompt
from com.github.dm0896665.main.ui.prompts.text_prompt import TextPrompt
from com.github.dm0896665.main.ui.prompts.yes_no_prompt import YesNoPrompt
from com.github.dm0896665.main.util.custom_ui_widgets import CustomGraphicsView
from com.github.dm0896665.main.util.player_util import PlayerUtil
from com.github.dm0896665.main.util.save_load_util import SaveLoadUtil
from com.github.dm0896665.main.util.ui_util import UiUtil
from com.github.dm0896665.main.util.ui_objects import CenteredWidget, Screen


class BattleStatus(Enum):
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    PLAYER_WON = "Player Won"
    MONSTER_WON = "Monster Won"
    RAN_AWAY = "Ran Away"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, battle_status: str):
        self.battle_status = battle_status

    def __str__(self):
        return self.battle_status

    def get_battle_status(self):
        return self.battle_status

class BattleSession:
    def __init__(self, is_practice):
        self.monster: Monster = None
        self.player: Player = None
        self.fail: int = 0
        self.round: int = 0
        self.battle_status: BattleStatus = BattleStatus.READY
        self.fast_attack_shown: bool = True
        self.large_attack_shown: bool = True
        self.choices_shown: bool = True
        self.switch_weapons_shown: bool = True
        self.view_stats_shown: bool = True
        self.run_shown: bool = True
        self.attacked_shown: bool = True

        if is_practice:
            self.fast_attack_shown = False
            self.large_attack_shown = False
            self.choices_shown = False
            self.switch_weapons_shown = False
            self.view_stats_shown = False
            self.run_shown: bool = False
            self.attacked_shown = False

class Battle(Screen):
    def __init__(self, is_practice: bool = False):
        super().__init__()
        self.pixmap_unscaled: QGraphicsPixmapItem = None
        self.starting_player_health: int = 0
        self.battle_session: BattleSession = BattleSession(is_practice)
        self.is_practice: bool = is_practice
        self.background_image: str = "background.png"

    def on_screen_did_show(self):
        self.battle_session.player = PlayerUtil.current_player
        self.assign_monster()
        self.show_monster()
        self.start()

    def show_monster(self):
        temp_monster: CustomGraphicsView  = CustomGraphicsView()
        UiUtil.load_monster_image(self.battle_session.monster.monster_name.lower().replace(" ", "_"), temp_monster)
        temp_monster_label: QLabel = QLabel()
        temp_monster_label.setText("A wild " + self.battle_session.monster.monster_name + " appears!")
        temp_monster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font: QFont = temp_monster_label.font()
        font.setPointSize(28)
        temp_monster_label.setFont(font)

        temp_monster_layout: QVBoxLayout = QVBoxLayout()
        temp_monster_layout.addWidget(temp_monster)
        temp_monster_layout.addWidget(temp_monster_label)

        # Set the layout of the Prompt
        temp_monster_container: CenteredWidget = CenteredWidget()
        temp_monster_container.setLayout(temp_monster_layout)
        UiUtil.show_widget_for_duration(temp_monster_container, 3)

    def on_battle_finished(self):
        if self.is_practice:
            OkayPrompt("After your " + str(self.battle_session.round) + " round fight, you would have " + str(self.battle_session.player.health) + "hp,\nbut since it was just practice we will reset your health back to " + str(self.starting_player_health) + "hp.")
            name_prompt: TextPrompt = TextPrompt("Before you get on to your journey, what should we call you?")
            name_prompt.valid_check_function: Callable[[str], bool] = self.name_prompt_check
            name_prompt.get_custom_invalid_prompt_text: Callable[[str], bool] = self.name_prompt_invalid_text
            name = name_prompt.show_and_get_results()
            PlayerUtil.current_player.name = name
        else:
            if self.battle_session.battle_status == BattleStatus.RAN_AWAY:
                OkayPrompt("Better luck next time!")

            OkayPrompt("After your " + str(self.battle_session.round) + " round fight, you have " + str(self.battle_session.player.health) + " hp, and your score is " + str(self.battle_session.player.score) + ".")

        print("Go to travel menu for " + PlayerUtil.current_player.name)

    def name_prompt_check(self, selected_option: str) -> bool:
        if selected_option == "":
            return False
        elif SaveLoadUtil.player_exists(selected_option):
            return False
        else:
            return True

    def name_prompt_invalid_text(self, selected_option: str) -> bool:
        if selected_option == "":
            return "Please enter you're character name."
        return "Sorry, the name '" + selected_option + "' is already taken."

    def assign_monster(self):
        if self.is_practice:
            self.battle_session.monster = Monster(MonsterType.PRACTICE_DUMMY)
        else:
            self.battle_session.monster = Monster()

    def resize_function(self, source, event: QResizeEvent):
        width: int = source.rect().width()
        self.ui.monster.setMaximumWidth(width/3 + width/20)
        self.ui.player.setMaximumWidth(width/3 + width/20)

    def start(self):
        monster: CustomGraphicsView = self.ui.monster
        player: CustomGraphicsView = self.ui.player
        width: int = self.ui.width()
        monster.setMaximumWidth(width/3 + width/20)
        player.setMaximumWidth(width/3 + width/20)

        monster.hide()
        UiUtil.load_monster_image(self.battle_session.monster.monster_name.lower().replace(" ", "_"), monster)
        UiUtil.toggle_visibility(monster)

        player.hide()
        UiUtil.load_player_image("player_facing_right", player)
        UiUtil.toggle_visibility(player)

        if self.is_practice:
            OkayPrompt("This is a simulated fight. You will not hurt your stats in any way, and if you beat the practice dummy you will get 10xp.\n However, in a real fight, if you die, you will lose 500xp, your health will be set to 500hp, and you will lose all of your on-hand coins.\n**So make sure you visit the bank and put all your money in it before you enter a fight!")
            OkayPrompt("When you fight monsters you can choose 1 of 5 things each round. You can either...\n1.) Do a fast attack\t2.) Do a Large attack\t3.) Run away from the fight\n4.) Switch which weapon you are using\t5.) View your current stats to help make a decision on what to do\n\nTry choosing some of the different options to see what they do.")

        monster: Monster = self.battle_session.monster
        OkayPrompt("The " + monster.monster_name + " starts out with " + str(monster.health) + " hp, and does " + str(monster.attack) + " damage at an attack rate of " + str(monster.attack_rate) + ".")

        if self.is_practice:
            OkayPrompt("When you fight monsters you can choose 1 of 5 things each round. You can either...\n1.) Do a fast attack\t2.) Do a Large attack\t3.) Run away from the fight\n4.) Switch which weapon you are using\t5.) View your current stats to help make a decision on what to do\n\nTry choosing some of the different options to see what they do.")

        self.starting_player_health = copy.deepcopy(self.battle_session.player.health)

        self.battle_session.battle_status = BattleStatus.IN_PROGRESS
        while self.battle_session.battle_status == BattleStatus.IN_PROGRESS:
            self.run_battle_round()

        match self.battle_session.battle_status:
            case BattleStatus.PLAYER_WON:
                self.player_won()
            case BattleStatus.MONSTER_WON:
                self.monster_won()

        self.on_battle_finished()

    def run_battle_round(self):
        attack_options = [MenuOption.FAST_ATTACK, MenuOption.LARGE_ATTACK]
        button_options = attack_options + [MenuOption.SWITCH_WEAPONS, MenuOption.RUN, MenuOption.VIEW_STATS]

        choice: MenuOption = Menu(2, *button_options).show_and_get_results()

        if choice in attack_options:
            self.do_attack(choice)
            self.do_monster_attack()
        else:
            self.do_nonattack(choice)

        self.battle_session.round+=1

    def do_attack(self, choice: MenuOption):
        should_attack: bool = True
        if self.battle_session.player.math.is_math_enabled:
            # TODO:Implement math here
            should_attack = True
        else:
            should_attack = True

        if should_attack:
            weapon: Weapon = self.battle_session.player.selected_weapon
            damage: int = 0

            if choice == MenuOption.FAST_ATTACK:
                if not self.battle_session.fast_attack_shown:
                    OkayPrompt("Note that Fast attacks will do a random number between 1 and the attack rate number of your selected weapon * the damage number of your weapon's damage.\nSo try to only use this if you have a high attack rate with your selected weapon type.")
                    self.battle_session.fast_attack_shown = True

                number_of_attacks: int = random.randint(1, weapon.attack_rate)
                damage = weapon.damage * number_of_attacks
                damage = self.crit(damage)
                plural: str = "s" if number_of_attacks > 1 else ""
                OkayPrompt("You do " + str(number_of_attacks) + " fast attack" + plural + " with your " + weapon.weapon_name + ", dealing " + str(damage) + " damage.")
            elif choice == MenuOption.LARGE_ATTACK:
                if not self.battle_session.large_attack_shown:
                    OkayPrompt("Note that Large attacks will do your selected weapon's damage + an attack boost between 0 and 3x your weapon's damage.\nSo try to only use this if you have a low attack rate with your selected weapon type.")
                    self.battle_session.large_attack_shown = True

                attack_boost: int = random.randint(0, weapon.damage*3)
                damage = weapon.damage + attack_boost
                OkayPrompt("With a " + str(attack_boost) + " attack boost, you use your " + weapon.weapon_name + " to deal " + str(damage) + " damage.")

            self.battle_session.monster.health -= damage
            OkayPrompt("The " + self.battle_session.monster.monster_name + " now has " + str(self.battle_session.monster.health) + "hp.")
        else:
            OkayPrompt("You were not able to do your attack, but the " + self.battle_session.monster.monster_name + " still makes an attack.")

    def crit(self, damage: int):
        random_int: int = random.randint(0, 3)
        if random_int == 3:
            return damage * 2
        else:
            return damage

    def do_nonattack(self, choice: MenuOption):
        match choice:
            case MenuOption.SWITCH_WEAPONS:
                if not self.battle_session.switch_weapons_shown:
                    OkayPrompt("In battle, you can switch to different weapons. This would be a good option to pick if you forgot to equip a certain weapon.")
                    self.battle_session.switch_weapons_shown = True
                WeaponUtil.switch_weapon()
            case MenuOption.VIEW_STATS:
                if not self.battle_session.view_stats_shown:
                    OkayPrompt("You can view your stats during battle to, make sure that you don't have any coins on you, make sure your health is high enough,\nor for any other reason that will help you make a decision on what to do next in battle.")
                    self.battle_session.view_stats_shown = True
                PlayerUtil.show_current_stats()
            case MenuOption.RUN:
                if not self.battle_session.run_shown:
                    should_run: PromptOption = YesNoPrompt("This is a smart option to pick if you don't think that you can beat a monster and you don't want to hurt your stats,\nbut this is a simulated fight. It can't hurt your stats, and if you beat the practice dummy you get 10xp.\nDo you still want to run?").show_and_get_results()
                    self.battle_session.run_shown = True
                    if should_run == PromptOption.NO:
                        return

                self.run_away()

    def run_away(self):
        OkayPrompt("You run away as fast as you can, but the " + self.battle_session.monster.monster_name + " does 150 damage to you as you run away.")
        self.battle_session.player.health -= 150
        self.battle_session.battle_status = BattleStatus.RAN_AWAY

    def do_monster_attack(self):
        monster: Monster = self.battle_session.monster

        if not self.battle_session.attacked_shown:
            OkayPrompt("Everytime that you do an attack the monster has a chance of doing an attack back.\nThey do their damage times a random number between 0 and their attack rate, and every attack they do has a 25% chance of getting a 2x crit.")
            self.battle_session.attacked_shown = True

        if monster.health <= 0:
            self.battle_session.battle_status = BattleStatus.PLAYER_WON
        else:
            damage: int = monster.attack * random.randint(0, monster.attack_rate)
            damage = self.crit(damage)
            self.battle_session.player.health -= damage
            health: str = str(self.battle_session.player.health)

            if damage == monster.attack:
                OkayPrompt("The monster strikes back with a(n) " + str(damage) + " damage attack. You now have " + health + " hp.")
            elif damage == 0:
                OkayPrompt("The monster misses and does 0 damage.")
            else:
                OkayPrompt("The monster strikes back with a crit attack of " + str(damage) + ". You now have " + health + " hp.")

            if self.battle_session.player.health <= 0:
                self.battle_session.battle_status = BattleStatus.MONSTER_WON

    def player_won(self):
        UiUtil.toggle_visibility(self.ui.monster)

        if self.is_practice:
            xp: int = 10
            OkayPrompt("Great job on that practice dummy! You've earned " + str(xp) + "xp!")
            self.battle_session.player.score+=xp
        else:
            monster: Monster = self.battle_session.monster
            money: int = (((monster.get_original_health() + monster.attack) * monster.attack_rate) / 10) + 50
            score: int = (monster.get_original_health() * random.randint(0, monster.attack_rate)) + 100;

            OkayPrompt("You have defeated the " + monster.monster_name + "! Great job!" +
                       "\n+" + str(money) + " coins." +
                       "\n+" + str(score) + " xp.")
            self.battle_session.player.money += money
            self.battle_session.player.score += score

            weapon_drops = WeaponUtil.weapon_drop(monster)
            if len(weapon_drops) > 0:
                weapon_helper_text: str = "these weapons" if len(weapon_drops) > 1 else "this weapon"
                weapon_text: str = ""
                for i, weapon in weapon_drops:
                    weapon_text = str(weapon)
                    if i != len(weapon_drops) - 1:
                        weapon_text = weapon_text + "\n"

                OkayPrompt("Looks like the monster dropped " + weapon_helper_text + ": \n" + weapon_text)
            self.battle_session.player.kills += 1

    def monster_won(self):
        UiUtil.toggle_visibility(self.ui.player)

        if self.is_practice:
            OkayPrompt(
                "You would have died right now, but since it is practice we will just send you back to the menu.")
        else:
            OkayPrompt("You have perished during a(n) " + str(self.battle_session.round) + " battle, better luck next time." +
                       "\nYour score was " + str(self.battle_session.player.score) +
                       "\nYou had " + str(self.battle_session.player.money) + "coins on you that the monster stole." +
                       "\nYou will loose 500xp; your health will be set to 500h, and you will return to the Travel Menu.")
            self.battle_session.player.deaths += 1
