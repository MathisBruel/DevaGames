import os
from flask import Flask
from app.config import Config


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
    
    return app
