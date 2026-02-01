from typing import Optional
from app.game.Game import Game


class Session:
    def __init__(self, id_session: str, game: Game):
        self.id_session = id_session
        self.game = game
        self.created_at = None
        self.last_activity = None

    def get_game_state(self):
        return self.game.get_game_state()

    def start_game(self, min_rounds: int, max_rounds: int):
        return self.game.start_game(min_rounds, max_rounds)

    def submit_answer(self, player_name: str, answer: str):
        return self.game.submit_answer(player_name, answer)

    def is_finished(self):
        return self.game.is_finished

    def is_started(self):
        return self.game.is_started