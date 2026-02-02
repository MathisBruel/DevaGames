import uuid
from typing import Dict, Optional, List
from app.game.Session import Session
from app.game.Game import Game
from app.game.Player import Player
from app.game.QuizEngine import QuizEngine


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, player_names: List[str] = None, quiz: Optional[QuizEngine] = None) -> str:
        if quiz is None:
            quiz = QuizEngine()
        
        # Game init no longer takes players
        game = Game(quiz=quiz)
        
        if player_names:
            for name in player_names:
                game.add_player(name)
                
        session_id = str(uuid.uuid4())
        session = Session(id_session=session_id, game=game)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions

    def get_all_sessions(self) -> Dict[str, Session]:
        return self.sessions.copy()

    def cleanup_finished_sessions(self):
        finished_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_finished()
        ]
        for session_id in finished_sessions:
            self.delete_session(session_id)
