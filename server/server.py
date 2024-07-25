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
                self.db.player_conn[req["username"]] = conn
                self.db.waiting_players.put(req["username"])
                if self.db.waiting_players.qsize() <= 1:
                    res = {"action": "ACK"}
                    self.send_res(res, conn)
                else:
                    # start a new game if there are two players in the queue
                    player_x = self.db.waiting_players.get()
                    player_o = self.db.waiting_players.get()
                    game = Game()
                    game.set_players(player_x=player_x, player_o=player_o)
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
                        "is_turn": False,
                    }
                    self.send_res(res, self.db.player_conn[player_o])
            case "move":
                game = self.db.games[req["game_id"]]
                game.move(x=req["x"], y=req["y"], chess=req["chess"])
                if req["chess"] == "X":
                    res = {
                        "action": "move",
                        "game_id": game.id,
                        "x": req["x"],
                        "y": req["y"],
                        "chess": "X",
                    }
                    self.send_res(res, self.db.player_conn[game.chess_player["O"]])
                else:
                    res = {
                        "action": "move",
                        "game_id": game.id,
                        "x": req["x"],
                        "y": req["y"],
                        "chess": "O",
                    }
                    self.send_res(res, self.db.player_conn[game.chess_player["X"]])
