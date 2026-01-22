from app.game import Player, QuizEngine, Quest


class Game:
    def __init__(self, players: [Player], quiz: QuizEngine):
        self.players = players
        self.quiz: QuizEngine = quiz
        self.current_question: Quest = None
