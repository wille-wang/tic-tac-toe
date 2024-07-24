import argparse
import socket
import threading
import json
import uuid
from queue import Queue

player_conn = {}
waiting_players = Queue()
games = {}

class Game():
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.chess_player = {"X": None, "O": None}
        self.board = [" " for _ in range(9)]
        self.current_turn = "X"
        self.winner = None
    
    def set_players(self, player_x: str, player_o: str):
        # TODO: add pseudorandomness
        self.chess_player["X"] = player_x
        self.chess_player["O"] = player_o
    
    def move(self, player, cell):
        if self.board[cell] == " " and player == self.current_turn:
            self.board[cell] = player
            self.current_turn = "O" if player == "X" else "X"
            self.check_board()
            return True
    
    def check_board(self):
        """check if there is a winner or a draw
        """
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
            (0, 4, 8), (2, 4, 6)              # diagonals
        ]
        for (a, b, c) in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.winner = self.board[a]
                return
        if all(cell != " " for cell in self.board):
            self.winner = "Draw"
    
    def get_game_state(self):
        """get the current state of the game

        Returns:
            dict: current game state of the game
        """
        return {
            "board": self.board,
            "current_turn": self.current_turn,
            "winner": self.winner,
        }

def receive_req(conn: socket.socket, addr: str):
    """receive and handle the request from the client

    Args:
        conn (socket.socket): connection object corresponding to each client
        addr (str): address of the client
    """
    # receive the request from the client
    while True:
        req = conn.recv(1_000)
        req = json.loads(req.decode())

        # handle the request
        match(req["action"]):
            case "register":
                player_conn[req["username"]] = conn
                waiting_players.put(req["username"])
                if waiting_players.qsize() <= 1:
                    res = {
                        "action": "ACK"
                    }
                    conn.sendall(json.dumps(res).encode())
                else:
                    # start a new game if there are two players in the queue
                    player_x = waiting_players.get()
                    player_o = waiting_players.get()
                    game = Game()
                    game.set_players(player_x=player_x, player_o=player_o)
                    games[game.id] = game.id

                    res = {
                        "action": "start_game",
                        "game_id": game.id,
                        "opponent": player_o,
                        "chess": "X"
                    }
                    player_conn[player_x].sendall(json.dumps(res).encode())
                    res = {
                        "action": "start_game",
                        "game_id": game.id,
                        "opponent": player_x,
                        "chess": "O"
                    }
                    player_conn[player_o].sendall(json.dumps(res).encode())

def start_server(host: str, port: int):
    """start the multithreaded server

    Args:
        host (str): hostname or IP address of the server
        port (int): port number of the server to listen on
    """
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server is listening on {host}:{port}")

        # create a new thread for each client
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=receive_req,
                args=(conn, addr),
            )
            thread.start()

if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # start the server
    start_server(host=args.host, port=args.port)