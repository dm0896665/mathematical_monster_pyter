import pickle

from com.github.dm0896665.main.core.player.player import Player

class SaveLoadUtil:

    @staticmethod
    def save_player(player: Player):
        pickle.dump(player, open('saves/' + player.name + '.pkl', 'wb'))

    @staticmethod
    def load_player(player_name: str):
        return pickle.load(open('saves/' + player_name + '.pkl', 'rb'))