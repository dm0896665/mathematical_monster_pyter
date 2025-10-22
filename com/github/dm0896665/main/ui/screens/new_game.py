from typing import Callable

from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption
from com.github.dm0896665.main.ui.prompts.multichoice_prompt import MultichoicePrompt
from com.github.dm0896665.main.ui.prompts.okay_prompt import OkayPrompt
from com.github.dm0896665.main.ui.prompts.on_off_prompt import OnOffPrompt
from com.github.dm0896665.main.ui.prompts.text_prompt import TextPrompt
from com.github.dm0896665.main.ui.prompts.yes_no_prompt import YesNoPrompt
from com.github.dm0896665.main.ui.screens.battle import Battle
from com.github.dm0896665.main.ui.screens.travel_menu import TravelMenu
from com.github.dm0896665.main.util.player_util import PlayerUtil
from com.github.dm0896665.main.util.save_load_util import SaveLoadUtil
from com.github.dm0896665.main.util.ui_objects import Screen
from com.github.dm0896665.main.util.ui_util import UiUtil


class NewGame(Screen):
    def __init__(self):
        super().__init__()

    def on_screen_did_show(self):
        player: Player = PlayerUtil.current_player

        is_math_on: PromptOption = OnOffPrompt("Do you want to keep math on or turn it off?").show_and_get_results()
        player.math.is_math_enabled = is_math_on == PromptOption.ON

        upgrade_option: PromptOption = MultichoicePrompt("Would you like to upgrade your health or strength?", PromptOption.HEALTH, PromptOption.STRENGTH).show_and_get_results()
        if upgrade_option == PromptOption.HEALTH:
            player.health+=100
            OkayPrompt("Very well, we will increase your health. You now have " + str(player.health) + " hp.")
        else:
            player.strength+=50
            OkayPrompt("Very well, we will increase your strength. You now have " + str(player.strength) + " strength.")

        is_need_practice: PromptOption = YesNoPrompt("Do you want to have a practice fight?").show_and_get_results()
        if is_need_practice == PromptOption.YES:
            OkayPrompt("Good to hear, lets get started.")
            UiUtil.change_screen(Battle(True))
            return
        else:
            OkayPrompt("Okay, no worries")

        name_prompt: TextPrompt = TextPrompt("Before you get on to your journey, what should we call you?")
        name_prompt.valid_check_function: Callable[[str], bool] = self.name_prompt_check
        name_prompt.get_custom_invalid_prompt_text: Callable[[str], bool] = self.name_prompt_invalid_text
        name = name_prompt.show_and_get_results()
        player.name = name

        UiUtil.change_screen(TravelMenu(True))

    def name_prompt_check(self, selected_option: str) -> bool:
        if selected_option == "":
            return False
        elif SaveLoadUtil.player_exists(selected_option):
            return False
        else:
            return True

    def name_prompt_invalid_text(self, selected_option: str) -> bool:
        if selected_option == "":
            return "Please enter your character name."
        return "Sorry, the name '" + selected_option + "' is already taken."