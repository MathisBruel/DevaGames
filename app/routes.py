from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response
import socket
import qrcode
import io
import base64
from app.game.SessionManager import SessionManager

bp = Blueprint('main', __name__)
session_manager = SessionManager()

# --- Helpers ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# --- Admin Routes ---
@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "admin":  # Simple password for now
            session['is_admin'] = True
            return redirect(url_for('main.admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Mot de passe incorrect")
    return render_template('admin_login.html')

@bp.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('main.admin_login'))
        
    if request.method == 'POST':
        # Create a new session (Lobby)
        session_id = session_manager.create_session(player_names=[])
        game_session = session_manager.get_session(session_id)
        
        # Read categories (checkboxes return list)
        categories = request.form.getlist('categories')
        if not categories:
            categories = ['culture_generale']  # Default
        
        # Read and apply config from form
        config = {
            'min_rounds': int(request.form.get('min_rounds', 5)),
            'max_rounds': int(request.form.get('max_rounds', 10)),
            'min_players': int(request.form.get('min_players', 2)),
            'max_players': int(request.form.get('max_players', 20)),
            'time_limit': int(request.form.get('time_limit', 30)),
            'difficulty_ratios': {
                'easy': int(request.form.get('ratio_easy', 10)),
                'normal': int(request.form.get('ratio_normal', 80)),
                'hard': int(request.form.get('ratio_hard', 10))
            },
            'categories': categories,
            'auto_advance': request.form.get('auto_advance') == 'on'
        }
        game_session.set_config(config)
        
        # Redirect to the Display page for this session (Projector view)
        return redirect(url_for('main.display_view', session_id=session_id))
        
    return render_template('admin_dashboard.html')

# --- Display Routes (Projector) ---
@bp.route('/display/<session_id>')
def display_view(session_id):
    if not session_manager.session_exists(session_id):
        return "Session not found", 404

    game_session = session_manager.get_session(session_id)
    state = game_session.get_game_state()
    
    # If game is playing or finished, show the Game View
    if state['status'] != "LOBBY":
        return render_template('display_game.html', state=state, session_id=session_id)

    # LOBBY: Generate QR Code for joining - Using SVG to avoid Pillow dependency
    import qrcode.image.svg
    
    local_ip = get_local_ip()
    join_url = f"http://{local_ip}:5000/join/{session_id}"
    
    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(join_url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=factory)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr = img_byte_arr.getvalue()
    # SVG is text/xml, but for data URI we can base64 it or just text it.
    # Base64 is safer for templates.
    qr_b64 = base64.b64encode(img_byte_arr).decode('utf-8')
    
    # Pass mime type to template if needed, or just assume svg+xml
    return render_template('display_lobby.html', session_id=session_id, qr_code=qr_b64, join_url=join_url, qr_type="image/svg+xml")

# --- Mobile Routes (Player) ---
@bp.route('/join/<session_id>', methods=['GET', 'POST'])
def join_page(session_id):
    if not session_manager.session_exists(session_id):
        return "Session introuvable", 404
        
    if request.method == 'POST':
        name = request.form.get('player_name')
        if name:
            game_session = session_manager.get_session(session_id)
            player = game_session.add_player(name)
            if player:
                # Success
                session['player_name'] = name
                session['game_session_id'] = session_id
                return redirect(url_for('main.mobile_controller'))
            else:
                # Full or error
                return render_template('mobile_join.html', session_id=session_id, error="Impossible de rejoindre (Lobby complet ?)")
        else:
             return render_template('mobile_join.html', session_id=session_id, error="Pseudo requis")
             
    return render_template('mobile_join.html', session_id=session_id)

@bp.route('/mobile/controller')
def mobile_controller():
    session_id = session.get('game_session_id')
    player_name = session.get('player_name')
    
    if not session_id or not player_name:
        return redirect(url_for('main.index')) # Or error page
        
    return render_template('mobile_controller.html', session_id=session_id, player_name=player_name)

# --- API Routes (Polling) ---
@bp.route('/api/game/<session_id>/state')
def api_game_state(session_id):
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
    return jsonify(game_session.get_game_state())


@bp.route('/api/game/<session_id>/start', methods=['POST'])
def api_start_game(session_id):
    # Admin/Display triggers this. Configuration is already set on Session Create.
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
        
    # We use the config already stored in the Game object
    # But start_game requires min/max args. We need to update Game.py to store them or fetch them here.
    # The clean way: Game stores config. start_game uses self.config.min_rounds.
    
    # Assuming we update Game.py to hold these values.
    # Let's assume start_game no longer needs args if they were set via set_config
    if not game_session.game.start_game(0, 0): # dummy args if implementation changes
         return jsonify({"error": "Failed to start (Min players not reached?)"}), 400
         
    return jsonify({"success": True})

@bp.route('/api/game/<session_id>/continue', methods=['POST'])
def api_continue_game(session_id):
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
        
    game_session.continue_game()
    return jsonify({"success": True})

@bp.route('/api/game/<session_id>/stop', methods=['POST'])
def api_stop_game(session_id):
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
        
    game_session.stop_game()
    return jsonify({"success": True})

@bp.route('/api/game/<session_id>/timeout', methods=['POST'])
def api_timeout(session_id):
    """Handle when time runs out - submit null answer and move to FEEDBACK."""
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
    
    # Get current player and submit a null/timeout answer
    current_player = game_session.game.get_current_player()
    if current_player and game_session.game.status == "PLAYING":
        # Submit wrong answer (empty string) to trigger FEEDBACK
        result = game_session.game.submit_answer(current_player.name, "__TIMEOUT__")
        return jsonify(result)
    
    return jsonify({"success": False, "message": "No active turn"})

@bp.route('/api/player/avatar/reroll', methods=['POST'])
def api_reroll_avatar():
    session_id = request.json.get('session_id')
    player_name = request.json.get('player_name')
    
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
        
    success = game_session.reroll_avatar(player_name)
    return jsonify({"success": success})

@bp.route('/api/player/<session_id>/<player_name>/avatar')
def api_get_player_avatar(session_id, player_name):
    """Get a player's current avatar URL."""
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
    
    # Find player in game
    for player in game_session.game.players:
        if player.name == player_name:
            return jsonify({"avatar_url": player.avatar.avatar_url})
    
    return jsonify({"error": "Player not found"}), 404

@bp.route('/api/game/<session_id>/answer', methods=['POST'])
def api_submit_answer(session_id):
    game_session = session_manager.get_session(session_id)
    if not game_session:
        return jsonify({"error": "No session"}), 404
        
    player_name = request.json.get('player_name')
    answer = request.json.get('answer')
    
    result = game_session.submit_answer(player_name, answer)
    return jsonify(result)

# Legacy / Default redirect
@bp.route('/')
def index():
    return redirect(url_for('main.admin_login'))

@bp.route('/about')
def about():
    return render_template('about.html')
