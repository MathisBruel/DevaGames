from typing import List, Optional, Dict
from app.game.Player import Player
from app.game.QuizEngine import QuizEngine, Quest


class Game:
    def __init__(self, players: List[Player], quiz: QuizEngine):
        self.players = players
        self.quiz: QuizEngine = quiz
        self.current_question: Optional[Quest] = None
        self.is_started = False
        self.is_finished = False
        self.current_round = 0
        self.max_rounds = 0
        self.current_player_index = 0
        self.waiting_for_answer = False

    def start_game(self, min_rounds: int, max_rounds: int, *args, **kwargs):
        if self.is_started:
            return False
        
        import random
        self.max_rounds = random.randint(min_rounds, max_rounds)
        self.is_started = True
        self.is_finished = False
        self.current_round = 1
        self.current_player_index = 0
        self.waiting_for_answer = False
        
        # Start first turn
        self.next_turn()
        return True

    def next_turn(self):
        if self.is_finished:
            return
        
        # If we were waiting for an answer and it hasn't been given (should not happen in normal flow if called correctly)
        # But here we are setting up the NEW question.
        
        player = self.get_current_player()
        if not player:
            return

        # Generate a new question for this player
        self.current_question = self.quiz.generate_question(difficulty="normal")
        self.waiting_for_answer = True

    def submit_answer(self, player_name: str, answer: str) -> Dict:
        if not self.is_started or self.is_finished:
            return {"valid": False, "message": "Game not active"}
        
        current_player = self.get_current_player()
        if current_player.name != player_name:
             return {"valid": False, "message": "Not your turn"}
        
        if not self.current_question:
             return {"valid": False, "message": "No active question"}

        is_correct = answer == self.current_question.answer
        points = 0
        if is_correct:
            points = self.current_question.multiplier * 10
            current_player.score += points
        
        # Determine next state
        next_player_index = self.current_player_index + 1
        
        result = {
            "valid": True,
            "correct": is_correct,
            "correct_answer": self.current_question.answer,
            "points": points,
            "player_score": current_player.score
        }

        if next_player_index >= len(self.players):
            # End of round
            if self.current_round >= self.max_rounds:
                self.is_finished = True
                self.waiting_for_answer = False
                self.current_question = None
            else:
                self.current_round += 1
                self.current_player_index = 0
                self.next_turn()
        else:
            # Next player
            self.current_player_index = next_player_index
            self.next_turn()
            
        return result

    def get_current_player(self) -> Optional[Player]:
        if not self.players or self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]

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
            "current_player": self.get_current_player().name if self.get_current_player() else None,
            "leaderboard": self.get_leaderboard()
        }

    def reset_game(self):
        self.is_started = False
        self.is_finished = False
        self.current_round = 0
        self.current_question = None
        self.current_player_index = 0
        for player in self.players:
            player.score = 0
