import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base pour l'application Flask"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuration de la base de données (si nécessaire)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///devagames.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
