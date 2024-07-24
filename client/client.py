import json
import socket
import threading
from board import Board


class Client:
    def __init__(self, host, port, username, board) -> None:
        # connect to the server
        self.host = host
        self.port = port
        self.username = username
        self.board = board
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"Connected to the server: {host}:{port}.")

        # start a thread to listen to the server
        self.listen_thread = threading.Thread(
            target=self.receive_res, daemon=True
        )
        self.listen_thread.start()

        self.register()

    def register(self):
        """send a registration request to the server"""
        req = {"username": self.username, "action": "register"}
        self.sock.sendall(json.dumps(req).encode())

    def process_res(self, res: dict):
        """handle the response from the server

        Args:
            res (dict): response from the server
        """
        # handle the response
        match res["action"]:
            case "start_game":
                self.game_id = res["game_id"]
                self.chess = res["chess"]
                self.board.status_label.setText(
                    f"{self.username} ({self.chess}) vs. {res['opponent']}"
                )
            # TODO: make a move

    def receive_res(self):
        """receive and handle the response from the server continuously"""
        try:
            while True:
                res = self.sock.recv(1_000)
                res = json.loads(res.decode())

                self.process_res(res=res)
                print(res)
        except json.JSONDecodeError:
            print(f"Disconnected from the server.")
            exit(1)
