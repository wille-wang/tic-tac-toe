import json
import socket
import sys
import argparse
import threading
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt

class TicTacToeClient(QMainWindow):
    def __init__(self, username, host, port):
        super().__init__()
        # game information
        self.username = username
        self.init_ui()
        self.game_id = None
        self.chess = None  # X or O

        # connect to the server
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"{username} has been connected to Server: {host}:{port}.")
        # start a thread to listen to the server
        self.listen_thread = threading.Thread(
            target=self.receive_res, daemon=True
        )
        self.listen_thread.start()

        self.register()

    def init_ui(self):
        """initialize the UI components for the board
        """
        self.setWindowTitle(f"Tic-Tac-Toe: {self.username}")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.status_label = QLabel("Connecting ...")
        self.layout.addWidget(self.status_label, 0, 0, 1, 3, Qt.AlignCenter)
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                button = QPushButton(" ")
                button.setFixedSize(100, 100)
                button.setFont(self.font())
                button.clicked.connect(lambda _, x=i, y=j: self.make_move(x, y))
                self.layout.addWidget(button, i+1, j)
                row.append(button)
            self.buttons.append(row)
    
    def register(self):
        """send a registration request to the server
        """
        req = {
            "username": self.username,
            "action": "register"
        }
        self.sock.sendall(json.dumps(req).encode())
    
    def receive_res(self):
        """receive and handle the response from the server continuously
        """
        while True:
            res = self.sock.recv(1_000)
            res = json.loads(res.decode())
            print(res)

            # handle the response
            match(res["action"]):
                case "start_game":
                    self.game_id = res["game_id"]
                    self.chess = res["chess"]
                    self.status_label.setText(
                        f"{self.username} ({self.chess}) vs. {res["opponent"]}"
                    )

if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # start the GUI application
    app = QApplication(sys.argv)
    client = TicTacToeClient(
        username=args.username,
        host=args.host,
        port=args.port
    )
    client.show()
    sys.exit(app.exec())