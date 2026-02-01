from typing import List, Optional, Dict
from app.game.Player import Player
from app.game.QuizEngine import QuizEngine, Quest


class Game:
    def __init__(self, players: List[Player], quiz: QuizEngine):
        self.players = players
        self.quiz: QuizEngine = quiz
        self.current_question: Optional[Quest] = None
        self.question_index = 0
        self.questions: List[Quest] = []
        self.is_started = False
        self.is_finished = False
        self.player_answers: Dict[str, Optional[str]] = {}
        self.current_round = 0
        self.max_rounds = 10

    def start_game(self, easy_count: int = 3, medium_count: int = 4, hard_count: int = 3):
        if self.is_started:
            return False
        self.questions = self.quiz.generate_mixed_questions(easy_count, medium_count, hard_count)
        if not self.questions:
            return False
        self.is_started = True
        self.is_finished = False
        self.question_index = 0
        self.current_round = 1
        self.current_question = self.questions[0] if self.questions else None
        self.player_answers = {player.name: None for player in self.players}
        return True

    def get_current_question(self) -> Optional[Quest]:
        return self.current_question

    def submit_answer(self, player_name: str, answer: str) -> bool:
        if not self.is_started or self.is_finished:
            return False
        if not self.current_question:
            return False
        if player_name not in [p.name for p in self.players]:
            return False
        if self.player_answers.get(player_name) is not None:
            return False
        self.player_answers[player_name] = answer
        return True

    def all_players_answered(self) -> bool:
        return all(answer is not None for answer in self.player_answers.values())

    def process_answers(self) -> Dict[str, Dict]:
        if not self.current_question:
            return {}
        results = {}
        for player in self.players:
            player_answer = self.player_answers.get(player.name)
            is_correct = player_answer == self.current_question.answer
            points = 0
            if is_correct:
                points = self.current_question.multiplier * 10
                player.score += points
            results[player.name] = {
                "answer": player_answer,
                "correct": is_correct,
                "points": points,
                "total_score": player.score
            }
        return results

    def next_question(self) -> bool:
        if not self.is_started or self.is_finished:
            return False
        if self.current_round >= self.max_rounds:
            self.is_finished = True
            return False
        self.question_index += 1
        if self.question_index >= len(self.questions):
            self.is_finished = True
            return False
        self.current_question = self.questions[self.question_index]
        self.current_round += 1
        self.player_answers = {player.name: None for player in self.players}
        return True

    def get_leaderboard(self) -> List[Dict]:
        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        return [
            {
                "name": player.name,
                "score": player.score,
                "avatar_url": player.avatar.avatar_url
            }
            for player in sorted_players
        ]

    def get_game_state(self) -> Dict:
        return {
            "is_started": self.is_started,
            "is_finished": self.is_finished,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "current_question": self.current_question.to_dict() if self.current_question else None,
            "players_answered": {name: answer is not None for name, answer in self.player_answers.items()},
            "leaderboard": self.get_leaderboard()
        }

    def reset_game(self):
        self.is_started = False
        self.is_finished = False
        self.question_index = 0
        self.current_round = 0
        self.current_question = None
        self.questions = []
        self.player_answers = {}
        for player in self.players:
            player.score = 0
