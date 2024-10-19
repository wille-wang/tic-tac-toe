import socket
import threading
import json
from database import Database


class Server:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.db = Database()
        self._start_multithreaded_server()

    def _start_multithreaded_server(self) -> None:
        """Start the multithreaded server"""

        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server is listening on {self.host}:{self.port}")

            # create a new thread for each client
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(
                    target=self._receive_req,
                    args=(conn, addr),
                )
                thread.start()
                print(f"Connected to {addr}.")

    def _receive_req(self, conn: socket.socket, addr: str) -> None:
        """Receive and handle the request from the client

        Args:
            conn (socket.socket): connection object corresponding to each client
            addr (str): address of the client
        """

        # Receive the request from the client
        try:
            while True:
                req = conn.recv(1_000)
                req = json.loads(req.decode())
                print(req)
                self._handle_req(req=req, conn=conn)

        except json.JSONDecodeError:
            print(f"{conn} disconnected.")
            # TODO: notify the opponent

    def _send_res(self, res: dict, conn: socket.socket) -> None:
        """Send the response to the client

        Args:
            res (dict): response to be sent to the client
            conn (socket.socket): connection object corresponding to each client
        """

        try:
            conn.sendall(json.dumps(res).encode())
        except Exception:
            print(f"Failed to send the response to the client.")

    def _handle_req(self, req: json, conn: socket.socket) -> None:
        """Handle the request from the client

        Args:
            req (json): decoded request from the client
            conn (socket.socket): connection object corresponding to each client
        """

        match (req["action"]):
            case "register":
                self.db.add_player(username=req["username"], conn=conn)
                game_id, player_x, player_o = self.db.match()
                # Notify both players
                if game_id is not None:
                    res = {
                        "action": "start",
                        "game_id": game_id,
                        "opponent": player_o,
                        "chess": "X",
                        "is_turn": True,
                    }
                    self._send_res(res, self.db.player_conn[player_x])
                    res = {
                        "action": "start",
                        "game_id": game_id,
                        "opponent": player_x,
                        "chess": "O",
                    }
                    self._send_res(res, self.db.player_conn[player_o])
            case "move":
                game = self.db.games[req["game_id"]]
                game.move(x=req["x"], y=req["y"], chess=req["chess"])
                # Notify the opponent
                res = {
                    "action": "move",
                    "x": req["x"],
                    "y": req["y"],
                    "winner": game.winner,
                    "is_end": self.db.games[game.id].is_end,
                }
                if req["chess"] == "X":
                    self._send_res(
                        res=res, conn=self.db.player_conn[game.chess_player["O"]]
                    )
                    # Notify the other player if the game is over
                    if game.is_end:
                        self._send_res(
                            res=res, conn=self.db.player_conn[game.chess_player["X"]]
                        )
                        self.db.games.pop(game.id)
                else:
                    self._send_res(
                        res=res, conn=self.db.player_conn[game.chess_player["X"]]
                    )
                    # Notify the other player if the game is over
                    if game.is_end:
                        self._send_res(
                            res=res, conn=self.db.player_conn[game.chess_player["O"]]
                        )
                        self.db.games.pop(game.id)
            case "exit":
                # Remove the player from the queue if he is waiting
                if self.db.waiting_players.qsize() > 0:
                    self.db.waiting_players.get()
                else:
                    game = self.db.games[req["game_id"]]

                    game.winner = "O" if req["chess"] == "X" else "X"
                    res = {"action": "surrender"}
                    if req["chess"] == "X":
                        self._send_res(
                            res=res, conn=self.db.player_conn[game.chess_player["O"]]
                        )
                        self.db.remove_player(game.chess_player["X"])
                    else:
                        self._send_res(
                            res=res, conn=self.db.player_conn[game.chess_player["X"]]
                        )
                        self.db.remove_player(game.chess_player["O"])
                    self.db.remove_game(req["game_id"])
                print(f"{req['username']} disconnected.")
