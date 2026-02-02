import random

class Player:
    def __init__(self, name: str, score: int = 0, id_session: str = None):
        self.name = name
        self.score = score
        self.id_session = id_session
        self.avatar = Avatar(self)

class Avatar:
    def __init__(self, player:Player):
        self.player = player
        self.avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={self.player.name}"
    
    def regenerate_avatar(self):
        self.avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={self.player.name}_{random.randint(0, 1000000)}"
    
    def __str__(self) -> str:
        return f"Avatar: {self.avatar_url}"

    def __repr__(self) -> str:
        return f"Avatar: {self.avatar_url}"

    def __eq__(self, other: 'Avatar') -> bool:
        return self.avatar_url == other.avatar_url

    def __hash__(self) -> int:
        return hash(self.avatar_url)