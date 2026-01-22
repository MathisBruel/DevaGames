import httpx
import random


class Quest:
    def __init__(self, question -> str, answer -> str, options -> list[str]):
        self.question = question
        self.answer = answer
        self.options = options

class EasyQuestion(Quest):
    def __init__(self, question -> str, answer -> str, options -> list[str]):
        super().__init__(question, answer, options)
        self.difficulty = "easy"
        self.multiplier = 1

class MediumQuestion(Quest):
    def __init__(self, question -> str, answer -> str, options -> list[str]):
        super().__init__(question, answer, options)
        self.difficulty = "medium"
        self.multiplier = 2

class HardQuestion(Quest):
    def __init__(self, question -> str, answer -> str, options -> list[str]):
        super().__init__(question, answer, options)
        self.difficulty = "hard"
        self.multiplier = 3

class QuizEngine:
    def __init__(self):
        self.api_url = "https://quizzapi.jomoreschi.fr/api/v2/quiz"
