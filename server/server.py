import socket
import threading
import json
from database import Database
from game import Game


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.db = Database()
        self.start_multithreaded_server()

    def start_multithreaded_server(self):
        """start the multithreaded server"""
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server is listening on {self.host}:{self.port}")

            # create a new thread for each client
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(
                    target=self.receive_req,
                    args=(conn, addr),
                )
                thread.start()
                print(f"Connected to {addr}.")

    def receive_req(self, conn: socket.socket, addr: str):
        """receive and handle the request from the client

        Args:
            conn (socket.socket): connection object corresponding to each client
            addr (str): address of the client
        """
        # receive the request from the client
        try:
            while True:
                req = conn.recv(1_000)
                req = json.loads(req.decode())
                print(req)
                self.handle_req(req=req, conn=conn)

        except json.JSONDecodeError:
            print(f"{conn} disconnected.")
            # TODO: notify the opponent

    def send_res(self, res: dict, conn: socket.socket):
        """send the response to the client

        Args:
            res (dict): response to be sent to the client
            conn (socket.socket): connection object corresponding to each client
        """
        try:
            conn.sendall(json.dumps(res).encode())
        except Exception:
            print(f"Failed to send the response to the client.")

    def handle_req(self, req: json, conn: socket.socket):
        """handle the request from the client

        Args:
            req (json): decoded request from the client
            conn (socket.socket): connection object corresponding to each client
        """
        match(req["action"]):
            case "register":
                # add the player to the queue
                self.db.player_conn[req["username"]] = conn
                self.db.waiting_players.put(req["username"])

                if self.db.waiting_players.qsize() >= 2:
                    # start a new game if there are two players in the queue
                    player_x = self.db.waiting_players.get()
                    player_o = self.db.waiting_players.get()
                    game = Game(player_x=player_x, player_o=player_o)
                    self.db.games[game.id] = game

                    # notify both players
                    res = {
                        "action": "start",
                        "game_id": game.id,
                        "opponent": player_o,
                        "chess": "X",
                        "is_turn": True,
                    }
                    self.send_res(res, self.db.player_conn[player_x])
                    res = {
                        "action": "start",
                        "game_id": game.id,
                        "opponent": player_x,
                        "chess": "O",
                    }
                    self.send_res(res, self.db.player_conn[player_o])
            case "move":
                game = self.db.games[req["game_id"]]
                game.move(x=req["x"], y=req["y"], chess=req["chess"])
                
                # notify the opponent
                res = {
                        "action": "move",
                        "x": req["x"],
                        "y": req["y"],
                        "winner": game.winner,
                        "is_end": self.db.games[game.id].is_end,
                    }
                if req["chess"] == "X":
                    self.send_res(
                        res=res,
                        conn=self.db.player_conn[game.chess_player["O"]]
                    )
                    # notify the other player if the game is over
                    if game.is_end:
                        self.send_res(
                            res=res,
                            conn=self.db.player_conn[game.chess_player["X"]]
                        )
                        self.db.games.pop(game.id)
                else:
                    self.send_res(
                        res=res,
                        conn=self.db.player_conn[game.chess_player["X"]]
                    )
                    # notify the other player if the game is over
                    if game.is_end:
                        self.send_res(
                            res=res, 
                            conn=self.db.player_conn[game.chess_player["O"]]
                        )
                        self.db.games.pop(game.id)
            case "exit":
                # remove the player from the queue if he is waiting
                if self.db.waiting_players.qsize() > 0:
                    self.db.waiting_players.get()
                else:
                    game = self.db.games[req["game_id"]]

                    game.winner = "O" if req["chess"] == "X" else "X"
                    res = {
                        "action": "surrender"
                    }
                    if req["chess"] == "X":
                        self.send_res(
                            res=res,
                            conn=self.db.player_conn[game.chess_player["O"]]
                        )
                    else:
                        self.send_res(
                            res=res,
                            conn=self.db.player_conn[game.chess_player["X"]]
                        )
                    self.db.games.pop(game.id)
                print(f"{req['username']} disconnected.")
