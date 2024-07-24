import socket
import threading
import json
from queue import Queue
from game import Game

player_conn = {}
waiting_players = Queue()
games = {}


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
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
                self.process_req(req=req, conn=conn)

        except json.JSONDecodeError:
            print(f"{conn} disconnected.")

    def process_req(self, req, conn):
        match (req["action"]):
            case "register":
                player_conn[req["username"]] = conn
                waiting_players.put(req["username"])
                if waiting_players.qsize() <= 1:
                    res = {"action": "ACK"}
                    conn.sendall(json.dumps(res).encode())
                else:
                    # start a new game if there are two players in the queue
                    player_x = waiting_players.get()
                    player_o = waiting_players.get()
                    game = Game()
                    game.set_players(player_x=player_x, player_o=player_o)
                    games[game.id] = game

                    # notify both players
                    res = {
                        "action": "start_game",
                        "game_id": game.id,
                        "opponent": player_o,
                        "chess": "X",
                        "is_turn": True,
                    }
                    player_conn[player_x].sendall(json.dumps(res).encode())
                    res = {
                        "action": "start_game",
                        "game_id": game.id,
                        "opponent": player_x,
                        "chess": "O",
                        "is_turn": False,
                    }
                    player_conn[player_o].sendall(json.dumps(res).encode())
