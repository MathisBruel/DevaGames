import os
from flask import Flask
from app.config import Config
from app.game.QuizEngine import QuizEngine


def create_app(config_class=Config):
    """Factory function pour créer l'application Flask"""
    # Obtenir le chemin du répertoire parent (racine du projet)
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Enregistrer les blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    quiz = QuizEngine()

    easy = quiz.generate_questions(count=10, difficulty="facile")
    medium = quiz.generate_questions(count=10, difficulty="normal")
    hard = quiz.generate_questions(count=10, difficulty="difficile")
    mixed = quiz.generate_mixed_questions(easy_count=3, medium_count=4, hard_count=3)

    for e in easy:
        print(e)
    for m in medium:
        print(m)
    for h in hard:
        print(h)
    for m in mixed:
        print(m)

    return app
