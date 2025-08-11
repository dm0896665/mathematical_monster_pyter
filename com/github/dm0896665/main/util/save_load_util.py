import os
import pickle

from com.github.dm0896665.main.core.player.player import Player

class SaveLoadUtil:
    path: str = 'saves/'
    ext: str = '.pkl'

    @staticmethod
    def save_player(player: Player):
        pickle.dump(player, open(SaveLoadUtil.path + player.name + SaveLoadUtil.ext, 'wb'))

    @staticmethod
    def load_player(player_name: str):
        return pickle.load(open(SaveLoadUtil.path + player_name + SaveLoadUtil.ext, 'rb'))

    @staticmethod
    def player_exists(player_name: str):
        player_name: str = player_name.lower()
        return os.path.exists(SaveLoadUtil.path + player_name + SaveLoadUtil.ext)