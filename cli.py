import random
import sys
import os

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game.QuizEngine import QuizEngine, Quest
from app.game.Player import Player

class CLIGame:
    def __init__(self):
        self.quiz = QuizEngine()
        self.players = []
        self.rounds = 0
        self.current_round = 0

    def setup_game(self):
        print("=== Bienvenue dans Questions pour un Champion (CLI) ===")
        
        while True:
            try:
                num_players = int(input("Combien de joueurs? (Minimum 1): "))
                if num_players >= 1:
                    break
                print("Il faut au moins 1 joueur.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")

        for i in range(num_players):
            name = input(f"Nom du joueur {i + 1}: ")
            self.players.append(Player(name))

        print("\n--- Configuration des Rounds ---")
        while True:
            try:
                min_rounds = int(input("Nombre minimum de rounds: "))
                max_rounds = int(input("Nombre maximum de rounds: "))
                if 0 < min_rounds <= max_rounds:
                    break
                print("Configuration invalide. Min > 0 et Min <= Max.")
            except ValueError:
                print("Veuillez entrer des nombres valides.")

        self.rounds = random.randint(min_rounds, max_rounds)
        print(f"\nLa partie se jouera en {self.rounds} rounds !")
        input("Appuyez sur Entrée pour commencer...")

    def play_round(self, round_num):
        print(f"\n=== ROUND {round_num}/{self.rounds} ===")
        
        for player in self.players:
            print(f"\n-> Tour de {player.name}")
            
            question = self.quiz.generate_question(difficulty="normal")
            
            if not question:
                print("Erreur: Impossible de récupérer une question.")
                continue

            self.ask_question(player, question)

    def ask_question(self, player: Player, question: Quest):
        print(f"\nQUESTION: {question.question}")
        
        for idx, option in enumerate(question.options):
            print(f"  {idx + 1}. {option}")

        while True:
            try:
                choice = int(input("\nVotre réponse (1-4): "))
                if 1 <= choice <= 4:
                    selected_answer = question.options[choice - 1]
                    break
                print("Veuillez choisir un nombre entre 1 et 4.")
            except ValueError:
                print("Entrée invalide.")

        if selected_answer == question.answer:
            points = question.multiplier if hasattr(question, 'multiplier') else 1
            points *= 10
            
            player.score += points
            print(f"BONNE RÉPONSE ! (+{points} points)")
        else:
            print(f"MAUVAISE RÉPONSE. La bonne réponse était: {question.answer}")
        
        print(f"Score actuel de {player.name}: {player.score}")

    def show_results(self):
        print("\n=== FIN DE LA PARTIE ===")
        print("Classement final:")
        
        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        
        for idx, player in enumerate(sorted_players):
            print(f"{idx + 1}. {player.name} - {player.score} points")

        if sorted_players:
            print(f"\nFélicitations à {sorted_players[0].name} !")

    def run(self):
        try:
            self.setup_game()
            for r in range(1, self.rounds + 1):
                self.play_round(r)
            self.show_results()
        except KeyboardInterrupt:
            print("\nPartie interrompue.")
        finally:
            self.quiz.close()

if __name__ == "__main__":
    game = CLIGame()
    game.run()
