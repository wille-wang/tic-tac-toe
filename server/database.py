from queue import Queue


class Database:
    def __init__(self) -> None:
        self.player_conn = {}  # username-connection pairs
        self.waiting_players = Queue()
        self.games = {}
