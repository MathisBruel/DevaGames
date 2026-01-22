import httpx
import random
from typing import Optional, List, Dict


class Quest:
    """Classe de base représentant une question de quiz."""
    
    def __init__(self, question: str, answer: str, options: List[str]):
        """
        Initialise une question de quiz.
        
        Args:
            question: Le texte de la question.
            answer: La réponse correcte.
            options: Liste des options de réponse (incluant la bonne réponse).
        """
        self.question = question
        self.answer = answer
        self.options = options

    def to_dict(self) -> Dict:
        """
        Convertit la question en dictionnaire.
        
        Returns:
            Dictionnaire contenant la question, la réponse et les options.
        """
        return {
            "question": self.question,
            "answer": self.answer,
            "options": self.options
        }
    
    def __str__(self) -> str:
        """
        Convertit la question en chaîne de caractères.
        
        Returns:
            Chaîne de caractères contenant la question, la réponse et les options.
        """
        return f"Question: {self.question}\nRéponse: {self.answer}\nOptions: {self.options}"


class EasyQuestion(Quest):
    """Question de difficulté facile avec un multiplicateur de points de 1."""
    
    def __init__(self, question: str, answer: str, options: List[str]):
        """
        Initialise une question facile.
        
        Args:
            question: Le texte de la question.
            answer: La réponse correcte.
            options: Liste des options de réponse (incluant la bonne réponse).
        """
        super().__init__(question, answer, options)
        self.difficulty = "easy"
        self.multiplier = 1

    def to_dict(self) -> Dict:
        """
        Convertit la question en dictionnaire avec sa difficulté et son multiplicateur.
        
        Returns:
            Dictionnaire contenant la question, la réponse, les options, la difficulté et le multiplicateur.
        """
        data = super().to_dict()
        data["difficulty"] = self.difficulty
        data["multiplier"] = self.multiplier
        return data
    


class MediumQuestion(Quest):
    """Question de difficulté moyenne avec un multiplicateur de points de 2."""
    
    def __init__(self, question: str, answer: str, options: List[str]):
        """
        Initialise une question de difficulté moyenne.
        
        Args:
            question: Le texte de la question.
            answer: La réponse correcte.
            options: Liste des options de réponse (incluant la bonne réponse).
        """
        super().__init__(question, answer, options)
        self.difficulty = "medium"
        self.multiplier = 2

    def to_dict(self) -> Dict:
        """
        Convertit la question en dictionnaire avec sa difficulté et son multiplicateur.
        
        Returns:
            Dictionnaire contenant la question, la réponse, les options, la difficulté et le multiplicateur.
        """
        data = super().to_dict()
        data["difficulty"] = self.difficulty
        data["multiplier"] = self.multiplier
        return data


class HardQuestion(Quest):
    """Question de difficulté élevée avec un multiplicateur de points de 3."""
    
    def __init__(self, question: str, answer: str, options: List[str]):
        """
        Initialise une question difficile.
        
        Args:
            question: Le texte de la question.
            answer: La réponse correcte.
            options: Liste des options de réponse (incluant la bonne réponse).
        """
        super().__init__(question, answer, options)
        self.difficulty = "hard"
        self.multiplier = 3

    def to_dict(self) -> Dict:
        """
        Convertit la question en dictionnaire avec sa difficulté et son multiplicateur.
        
        Returns:
            Dictionnaire contenant la question, la réponse, les options, la difficulté et le multiplicateur.
        """
        data = super().to_dict()
        data["difficulty"] = self.difficulty
        data["multiplier"] = self.multiplier
        return data


class QuizEngine:
    """Moteur de quiz pour gérer l'API de questions et générer des questions pour un jeu type 'Question pour un champion'."""
    
    def __init__(self):
        """Initialise le moteur de quiz avec l'URL de l'API et un client HTTP."""
        self.api_url = "https://quizzapi.jomoreschi.fr/api/v2/quiz"
        self.client = httpx.Client(timeout=10.0)

    def fetch_questions(self, limit: int = 10, difficulty: Optional[str] = None, 
                       category: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Récupère des questions depuis l'API de quiz.
        
        Args:
            limit: Nombre de questions à récupérer (par défaut: 10).
            difficulty: Niveau de difficulté ("facile", "normal", "difficile") ou None pour tous.
            category: Catégorie de questions ou None pour toutes.
        
        Returns:
            Liste de dictionnaires contenant les données des questions, ou None en cas d'erreur.
        """
        params = {"limit": limit}
        if difficulty:
            params["difficulty"] = difficulty
        if category:
            params["category"] = category

        try:
            response = self.client.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("quizzes", [])
        except httpx.HTTPError as e:
            print(f"Erreur lors de la récupération des questions: {e}")
            return None

    def _create_question_object(self, api_question: Dict, difficulty: str) -> Quest:
        """
        Crée un objet Quest à partir des données de l'API.
        
        Args:
            api_question: Dictionnaire contenant les données de la question depuis l'API.
            difficulty: Niveau de difficulté de la question ("facile", "normal", "difficile").
        
        Returns:
            Objet Quest (EasyQuestion, MediumQuestion, HardQuestion ou Quest) avec les options mélangées.
        """
        question_text = api_question.get("question", "")
        correct_answer = api_question.get("answer", "")
        incorrect_answers = api_question.get("badAnswers", [])
        
        options = [correct_answer] + incorrect_answers
        random.shuffle(options)
        
        if difficulty == "facile":
            return EasyQuestion(question_text, correct_answer, options)
        elif difficulty == "normal":
            return MediumQuestion(question_text, correct_answer, options)
        elif difficulty == "difficile":
            return HardQuestion(question_text, correct_answer, options)
        else:
            return Quest(question_text, correct_answer, options)

    def generate_question(self, difficulty: str = "normal") -> Optional[Quest]:
        """
        Génère une seule question d'un niveau de difficulté donné.
        
        Args:
            difficulty: Niveau de difficulté ("facile", "normal", "difficile"). Par défaut: "normal".
        
        Returns:
            Objet Quest correspondant à la difficulté demandée, ou None en cas d'erreur.
        """
        questions_data = self.fetch_questions(limit=1, difficulty=difficulty)
        if not questions_data or len(questions_data) == 0:
            return None
        
        return self._create_question_object(questions_data[0], difficulty)

    def generate_questions(self, count: int = 10, difficulty: Optional[str] = None) -> List[Quest]:
        """
        Génère plusieurs questions d'un même niveau de difficulté.
        
        Args:
            count: Nombre de questions à générer (par défaut: 10).
            difficulty: Niveau de difficulté ("facile", "normal", "difficile") ou None pour un mélange.
        
        Returns:
            Liste d'objets Quest. Liste vide en cas d'erreur.
        """
        questions_data = self.fetch_questions(limit=count, difficulty=difficulty)
        if not questions_data:
            return []
        
        questions = []
        for q_data in questions_data:
            q_difficulty = q_data.get("difficulty", difficulty or "normal")
            question = self._create_question_object(q_data, q_difficulty)
            questions.append(question)
        
        return questions

    def generate_mixed_questions(self, easy_count: int = 3, medium_count: int = 4, 
                                 hard_count: int = 3) -> List[Quest]:
        """
        Génère un mélange de questions de différents niveaux de difficulté.
        
        Args:
            easy_count: Nombre de questions faciles (par défaut: 3).
            medium_count: Nombre de questions moyennes (par défaut: 4).
            hard_count: Nombre de questions difficiles (par défaut: 3).
        
        Returns:
            Liste d'objets Quest mélangés de différents niveaux de difficulté.
        """
        all_questions = []
        
        if easy_count > 0:
            easy_questions = self.generate_questions(easy_count, "facile")
            all_questions.extend(easy_questions)
        
        if medium_count > 0:
            medium_questions = self.generate_questions(medium_count, "normal")
            all_questions.extend(medium_questions)
        
        if hard_count > 0:
            hard_questions = self.generate_questions(hard_count, "difficile")
            all_questions.extend(hard_questions)
        
        random.shuffle(all_questions)
        return all_questions

    def close(self):
        """Ferme le client HTTP et libère les ressources."""
        self.client.close()

    def __del__(self):
        """Destructeur qui ferme le client HTTP si nécessaire."""
        if hasattr(self, 'client'):
            try:
                self.client.close()
            except:
                pass
