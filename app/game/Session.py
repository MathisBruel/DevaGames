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

    def start_game(self, easy_count: int = 3, medium_count: int = 4, hard_count: int = 3):
        return self.game.start_game(easy_count, medium_count, hard_count)

    def submit_answer(self, player_name: str, answer: str):
        return self.game.submit_answer(player_name, answer)

    def process_answers(self):
        return self.game.process_answers()

    def next_question(self):
        return self.game.next_question()

    def get_current_question(self):
        return self.game.get_current_question()

    def get_leaderboard(self):
        return self.game.get_leaderboard()

    def is_finished(self):
        return self.game.is_finished

    def is_started(self):
        return self.game.is_started

    def all_players_answered(self):
        return self.game.all_players_answered()