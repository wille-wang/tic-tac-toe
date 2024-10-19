from queue import Queue
from game import Game


class Database:
    def __init__(self) -> None:
        self.player_conn = {}  # username-connection pairs
        self.waiting_players = Queue()
        self.games = {}  # id-game pairs

    def add_player(self, username: str, conn) -> None:
        """Add a player to the database

        Args:
            username (str): username of the player
            conn (socket.socket): connection object corresponding to the player
        """

        self.player_conn[username] = conn
        self.waiting_players.put(username)

    def match(self) -> tuple[str, str, str]:
        """Match two players if there are enough players

        Returns:
            tuple[str, str, str]: game id, player_x, player_o
        """

        if self.waiting_players.qsize() >= 2:
            player_x = self.waiting_players.get()
            player_o = self.waiting_players.get()
            game = Game(player_x=player_x, player_o=player_o)
            self.games[game.id] = game
            return game.id, player_x, player_o
        else:
            return None, None, None

    def remove_player(self, username: str) -> None:
        """Remove a player from the database

        Args:
            username (str): username of the player
        """
        
        self.player_conn.pop(username)

    def remove_game(self, id: str) -> None:
        """Remove a game from the database

        Args:
            id (str): game id
        """

        self.games.pop(id)
