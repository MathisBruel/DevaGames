from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@bp.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html')
