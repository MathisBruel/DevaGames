# DevaGames - Application Flask

Application web Flask pour DevaGames.

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Sur Windows :
```bash
venv\Scripts\activate
```
- Sur Linux/Mac :
```bash
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` à la racine du projet :
```
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
```

## Lancement

Pour lancer l'application :

```bash
python main.py
```

L'application sera accessible sur `http://localhost:5000`

## Structure du projet

```
DevaGames/
├── app/
│   ├── __init__.py      # Factory de l'application Flask
│   ├── config.py        # Configuration de l'application
│   └── routes.py        # Routes de l'application
├── templates/
│   ├── base.html        # Template de base
│   ├── index.html       # Page d'accueil
│   └── about.html       # Page à propos
├── static/
│   ├── css/
│   │   └── style.css    # Styles CSS
│   ├── js/
│   │   └── main.js      # Scripts JavaScript
│   └── images/          # Images
├── main.py              # Point d'entrée de l'application
├── requirements.txt     # Dépendances Python
└── README.md           # Ce fichier
```

## Développement

L'application utilise une architecture modulaire avec :
- **Blueprints** pour organiser les routes
- **Factory pattern** pour créer l'application
- **Configuration** via variables d'environnement
- **Templates Jinja2** pour le rendu HTML

## Prochaines étapes

- Ajouter une base de données (SQLAlchemy)
- Implémenter l'authentification utilisateur
- Ajouter les fonctionnalités spécifiques à DevaGames
