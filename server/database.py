from queue import Queue


class Database:
    def __init__(self) -> None:
        self.player_conn = {}
        self.waiting_players = Queue()
        self.games = {}
