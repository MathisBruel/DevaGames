from typing import List, Optional, Dict
from app.game.Player import Player
from app.game.QuizEngine import QuizEngine, Quest
import random

class Game:
    def __init__(self, quiz: QuizEngine):
        self.players: List[Player] = []
        self.quiz: QuizEngine = quiz
        self.current_question: Optional[Quest] = None
        self.status = "LOBBY" # LOBBY, PLAYING, FEEDBACK, FINISHED
        self.current_round = 0
        self.max_rounds = 0
        self.time_limit = 30
        self.difficulty_ratios = {"easy": 10, "normal": 80, "hard": 10}
        self.auto_advance = False
        self.min_players = 2
        self.max_players = 100
        self.current_player_index = 0
        self.waiting_for_answer = False
        self.last_answer_result: Optional[Dict] = None

    def add_player(self, name: str) -> Optional[Player]:
        # Check if player already exists
        for p in self.players:
            if p.name == name:
                return p
        
        if len(self.players) >= self.max_players:
            return None # Game full
        
        new_player = Player(name)
        new_player.avatar.regenerate_avatar() # Random avatar on join
        self.players.append(new_player)
        return new_player

    def reroll_avatar(self, player_name: str) -> bool:
        for p in self.players:
            if p.name == player_name:
                p.avatar.regenerate_avatar()
                return True
        return False

    def set_config(self, config: Dict):
        """Sets configuration before game start"""
        self.min_players = config.get('min_players', 2)
        self.max_players = config.get('max_players', 100)
        self.time_limit = config.get('time_limit', 30)
        self.difficulty_ratios = config.get('difficulty_ratios', {"easy": 10, "normal": 80, "hard": 10})
        self.auto_advance = config.get('auto_advance', False)
        
        # Store categories and pass to QuizEngine
        self.categories = config.get('categories', [])
        if self.categories and self.quiz:
            self.quiz.set_categories(self.categories)
        
        # Store round config
        self._config_min_rounds = config.get('min_rounds', 5)
        self._config_max_rounds = config.get('max_rounds', 10)

    def start_game(self, min_rounds: int, max_rounds: int, *args, **kwargs):
        if self.status == "PLAYING":
            return False
            
        if len(self.players) < self.min_players:
            return False
        
        # Use stored config if args are 0 (which meant "use default/stored")
        if min_rounds == 0 and max_rounds == 0:
             effective_min = getattr(self, '_config_min_rounds', 5)
             effective_max = getattr(self, '_config_max_rounds', 10)
        else:
             effective_min = min_rounds
             effective_max = max_rounds
        
        self.max_rounds = random.randint(effective_min, effective_max)
        
        # Override config if passed via kwargs (unlikely now but safe to keep)
        if 'time_limit' in kwargs: self.time_limit = kwargs['time_limit']
        if 'difficulty_ratios' in kwargs: self.difficulty_ratios = kwargs['difficulty_ratios']
        if 'auto_advance' in kwargs: self.auto_advance = kwargs['auto_advance']
        
        self.status = "PLAYING"
        self.current_round = 1
        self.current_player_index = 0
        self.waiting_for_answer = False
        self.last_answer_result = None
        
        # Start first turn
        self.next_turn()
        return True

    def next_turn(self):
        if self.status == "FINISHED":
            return
        
        player = self.get_current_player()
        if not player:
            return

        # Select difficulty based on ratios
        difficulties = ["facile", "normal", "difficile"]
        weights = [
            self.difficulty_ratios.get("easy", 0),
            self.difficulty_ratios.get("normal", 0),
            self.difficulty_ratios.get("hard", 0)
        ]
        # Fallback if sum is 0
        if sum(weights) == 0:
            weights = [33, 33, 33]
            
        selected_diff = random.choices(difficulties, weights=weights, k=1)[0]

        # Generate a new question for this player
        self.current_question = self.quiz.generate_question(difficulty=selected_diff)
        self.waiting_for_answer = True
        self.status = "PLAYING"

    def submit_answer(self, player_name: str, answer: str) -> Dict:
        if self.status != "PLAYING":
            return {"valid": False, "message": "Game not active or in review"}
        
        current_player = self.get_current_player()
        if not current_player:
            return {"valid": False, "message": "No active player"}

        if current_player.name != player_name:
             return {"valid": False, "message": "Not your turn"}
        
        if not self.current_question:
             return {"valid": False, "message": "No active question"}

        # Convert letter answer (A, B, C, D) to actual option text
        actual_answer = answer
        letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        if answer in letter_map and self.current_question.options:
            idx = letter_map[answer]
            if idx < len(self.current_question.options):
                actual_answer = self.current_question.options[idx]
        
        is_correct = actual_answer == self.current_question.answer
        points = 0
        if is_correct:
            points = self.current_question.multiplier * 10
            current_player.score += points
        
        result = {
            "valid": True,
            "correct": is_correct,
            "correct_answer": self.current_question.answer,
            "points": points,
            "player_score": current_player.score,
            "player_name": current_player.name
        }
        
        self.last_answer_result = result
        self.status = "FEEDBACK" # Pause for feedback
        self.waiting_for_answer = False
            
        return result

    def continue_game(self):
        """Advances from FEEDBACK state to the next turn"""
        if self.status != "FEEDBACK":
            return False

        next_player_index = self.current_player_index + 1
        
        if next_player_index >= len(self.players):
             # End of round
            if self.current_round >= self.max_rounds:
                self.status = "FINISHED"
                self.current_question = None
            else:
                self.current_round += 1
                self.current_player_index = 0
                self.next_turn()
        else:
            # Next player
            self.current_player_index = next_player_index
            self.next_turn()
            
        return True

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
        # Blind Mode Logic: Active if past 50% of rounds
        is_blind_mode = False
        if self.max_rounds > 0 and self.current_round > (self.max_rounds / 2):
            is_blind_mode = True
            
        # Prepare Leaderboard
        leaderboard = self.get_leaderboard()
        
        # If Blind Mode is active AND game is not finished, corrupt the leaderboard
        if is_blind_mode and self.status != "FINISHED":
            # Shuffle to hide ranks
            random.shuffle(leaderboard)
            # Mask scores
            for p in leaderboard:
                p['score'] = "???"

        return {
            "status": self.status,
            "is_started": self.status in ["PLAYING", "FEEDBACK"], 
            "is_finished": self.status == "FINISHED",
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "time_limit": self.time_limit,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "auto_advance": self.auto_advance,
            "is_blind_mode": is_blind_mode,
            "current_question": self.current_question.to_dict() if self.current_question else None,
            "current_player": self.get_current_player().name if self.get_current_player() else None,
            "players_count": len(self.players),
            "leaderboard": leaderboard,
            "last_result": self.last_answer_result
        }

    def reset_game(self):
        self.status = "LOBBY"
        self.current_round = 0
        self.current_question = None
        self.current_player_index = 0
        self.last_answer_result = None
        self.players = [] # Reset players too? Usually yes for a new game session.

    def stop_game(self):
        """Forces the game to end immediately."""
        self.status = "FINISHED"
        self.current_question = None

