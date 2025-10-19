from com.github.dm0896665.main.core.player.player import Player
from com.github.dm0896665.main.ui.prompts.okay_prompt import OkayPrompt
from com.github.dm0896665.main.util.string_util import StringUtil


class PlayerUtil:
    current_player: Player = Player()

    @staticmethod
    def get_current_player():
        if PlayerUtil.current_player is not None:
            return PlayerUtil.current_player
        else:
            return Player()

    @staticmethod
    def show_current_stats():
        player = PlayerUtil.current_player
        math = player.math
        weapon = player.selected_weapon
        OkayPrompt(
            "Name: " + player.name
            + "\nMath questions answered correct: " + str(math.get_correct_answer_count()) + ", Math questions answered incorrect: " + str(math.get_incorrect_answer_count()) + ", Math C/I Ratio: " + str(math.get_ci_ratio()) + ", Math Question Total: " + str(math.get_total_questions_answered())
            + ", \nKills: " + str(player.kills) + ", Deaths: " + str(player.deaths) + ", K/D Ratio: " + str(player.get_kd()) + ", Health: " + str(player.health) + ", Strength: " + str(player.strength) + ", Score: " + str(player.score)
            + ", \nSelected Weapon: " + str(weapon)
            + ", \nCoins: " + str(player.money) + ", Bank: " + str(player.bank) + ", Upgrades: " + str(player.upgrades) + ", Math is: " + StringUtil.bool_to_on_off_str_capital(math.is_math_enabled))
