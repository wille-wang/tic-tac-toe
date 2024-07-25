import threading
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt
from client import Client


class Board(QMainWindow):
    """GUI for the Tic-Tac-Toe game"""

    def __init__(self, username, client: Client) -> None:
        super().__init__()
        # game information
        self.username = username
        self.game_id = None
        self.chess = None  # X or O
        self.client = client

        # Start a thread to handle server responses
        self.client_res_thread = threading.Thread(target=self.handle_res, daemon=True)
        self.client_res_thread.start()

        self.reset_board()
        self.register()

    def reset_board(self) -> None:
        """reset the board to the initial state"""
        self.setWindowTitle(f"Tic-Tac-Toe: {self.username}")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.status_label = QLabel("Waiting to connect ...")
        self.layout.addWidget(self.status_label, 0, 0, 1, 3, Qt.AlignCenter)
        self.buttons = []
        for x in range(3):
            row = []
            for y in range(3):
                button = QPushButton(" ")
                button.setFixedSize(100, 100)
                button.setFont(self.font())
                button.clicked.connect(lambda _, x=x, y=y: self.move(x, y))
                self.layout.addWidget(button, x + 1, y)
                row.append(button)
            self.buttons.append(row)

    def register(self) -> None:
        """register the player to the server"""
        self.client.send_req(req={"username": self.username, "action": "register"})
        self.status_label.setText(f"Connected. Waiting for an opponent ...")

    def move(self, x: int, y: int) -> None:
        """make a move on the board

        Args:
            x (int): index of the row
            y (int): index of the column
        """
        if self.chess:
            self.buttons[x][y].setText(self.chess)
            self.buttons[x][y].setEnabled(False)

        self.client.send_req(
            req={"game_id": self.game_id, "action": "move", "x": x, "y": y}
        )

    def handle_res(self):
        """handle the response from the server and modify the board

        Args:
            res (dict): response from the server
        """
        while True:
            res = self.client.received_res()
            # handle the response
            match res["action"]:
                case "start":
                    self.game_id = res["game_id"]
                    self.chess = res["chess"]
                    self.status_label.setText(
                        f"{self.username} ({self.chess}) vs. {res['opponent']}"
                    )
