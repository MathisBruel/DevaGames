from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.game.SessionManager import SessionManager

bp = Blueprint('main', __name__)
session_manager = SessionManager()

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Setup Game
        # Expecting form data: 'players' (comma separated names), 'min_rounds', 'max_rounds'
        # To make it dynamic, we might receive list of names.
        
        # Simple form handling:
        player_names_input = request.form.getlist('player_name')
        # Filter empty names
        player_names = [name.strip() for name in player_names_input if name.strip()]
        
        if not player_names:
            player_names = ["Joueur 1"] # Fallback

        try:
            min_rounds = int(request.form.get('min_rounds', 5))
            max_rounds = int(request.form.get('max_rounds', 10))
        except ValueError:
            min_rounds = 5
            max_rounds = 10

        # Create Session
        session_id = session_manager.create_session(player_names)
        
        # Start Game
        game_session = session_manager.get_session(session_id)
        if game_session:
            game_session.start_game(min_rounds, max_rounds)
            session['game_session_id'] = session_id
            return redirect(url_for('main.play'))
    
    return render_template('index.html')

@bp.route('/play')
def play():
    session_id = session.get('game_session_id')
    if not session_id or not session_manager.session_exists(session_id):
        return redirect(url_for('main.index'))
    
    game_session = session_manager.get_session(session_id)
    state = game_session.get_game_state()
    
    if state['is_finished']:
        return redirect(url_for('main.result'))
        
    return render_template('game.html', state=state)

@bp.route('/answer', methods=['POST'])
def answer():
    session_id = session.get('game_session_id')
    if not session_id:
        return jsonify({"error": "No session"}), 400
        
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "Session expired"}), 400
    
    player_name = request.form.get('player_name')
    answer = request.form.get('answer')
    
    result = game_session.submit_answer(player_name, answer)
    
    # If the call was an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result)
        
    # Standard form submit redirect
    if game_session.is_finished():
         return redirect(url_for('main.result'))
         
    return redirect(url_for('main.play'))

@bp.route('/result')
def result():
    session_id = session.get('game_session_id')
    if not session_id:
        return redirect(url_for('main.index'))
        
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return redirect(url_for('main.index'))
        
    state = game_session.get_game_state()
    return render_template('result.html', state=state)

@bp.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html')
