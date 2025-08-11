from com.github.dm0896665.main.core.player.player import Player


class PlayerUtil:
    current_player: Player = Player()

    @staticmethod
    def get_current_player():
        if PlayerUtil.current_player is not None:
            return PlayerUtil.current_player
        else:
            return Player()
