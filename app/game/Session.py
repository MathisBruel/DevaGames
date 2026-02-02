from typing import Optional, Dict
from app.game.Game import Game


class Session:
    def __init__(self, id_session: str, game: Game):
        self.id_session = id_session
        self.game = game
        self.created_at = None
        self.last_activity = None

    def get_game_state(self):
        return self.game.get_game_state()

    def add_player(self, name: str):
        return self.game.add_player(name)

    def set_config(self, config: Dict):
        self.game.set_config(config)

    def reroll_avatar(self, player_name: str) -> bool:
        return self.game.reroll_avatar(player_name)

    def start_game(self, min_rounds: int, max_rounds: int):
        return self.game.start_game(min_rounds, max_rounds)

    def continue_game(self):
        return self.game.continue_game()

    def stop_game(self):
        return self.game.stop_game()

    def submit_answer(self, player_name: str, answer: str):
        return self.game.submit_answer(player_name, answer)

    def is_finished(self):
        return self.game.status == "FINISHED"

    def is_started(self):
        return self.game.status in ["PLAYING", "FEEDBACK"]