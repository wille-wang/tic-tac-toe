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
        self.is_turn = False

        # Start a thread to handle server responses
        self.client_res_thread = threading.Thread(target=self._handle_res, daemon=True)
        self.client_res_thread.start()

        # Set up the board and register the player
        self._reset_board()
        self._register()

    def _reset_board(self) -> None:
        """Reset the board to the initial state"""

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
                button.setEnabled(True)
                button.setFixedSize(100, 100)
                button.setFont(self.font())
                button.clicked.connect(lambda _, x=x, y=y: self._move(x, y))
                self.layout.addWidget(button, x + 1, y)
                row.append(button)
            self.buttons.append(row)

        # rematch button
        self.rematch_button = QPushButton("Rematch")
        self.rematch_button.setFixedSize(100, 50)
        self.rematch_button.clicked.connect(self._rematch)
        self.layout.addWidget(self.rematch_button, 4, 0, 1, 1)

        # exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFixedSize(100, 50)
        self.exit_button.clicked.connect(self._exit)
        self.layout.addWidget(self.exit_button, 4, 2, 1, 1)

    def _register(self) -> None:
        """Register the player to the server"""

        self.client.send_req(
            req={
                "action": "register",
                "username": self.username,
            }
        )
        self._reset_board()
        self.rematch_button.setEnabled(False)
        self.status_label.setText(f"Connected. Waiting for an opponent ...")

    def _move(self, x: int, y: int) -> None:
        """Make a move on the board

        Args:
            x (int): index of the row
            y (int): index of the column
        """

        if self.chess and self.is_turn:
            self.buttons[x][y].setText(self.chess)
            self.buttons[x][y].setEnabled(False)
            self.is_turn = False

            self.client.send_req(
                req={
                    "action": "move",
                    "username": self.username,
                    "game_id": self.game_id,
                    "chess": self.chess,
                    "x": x,
                    "y": y,
                }
            )

    def _handle_res(self) -> None:
        """Handle the response from the server and modify the board

        Args:
            res (dict): response from the server
        """
        
        while True:
            res = self.client.received_res()
            # Handle the response
            match res["action"]:
                case "start":
                    self.game_id = res["game_id"]
                    self.chess = res["chess"]
                    self.status_label.setText(
                        f"{self.username} ({self.chess}) vs. {res['opponent']}"
                    )

                    if self.chess == "X":
                        self.is_turn = res["is_turn"]
                case "move":
                    x, y = res["x"], res["y"]
                    if self.chess == "X":
                        self.buttons[x][y].setText("O")
                    else:
                        self.buttons[x][y].setText("X")
                    self.buttons[x][y].setEnabled(False)
                    self.is_turn = True

                    if res["is_end"]:
                        if res["winner"] == self.chess:
                            self.buttons[x][y].setText(self.chess)
                            self.status_label.setText(f"Game over. You won!")
                        elif res["winner"]:
                            self.status_label.setText(f"Game over. You lost.")
                        else:
                            self.status_label.setText(f"Game over. It's a draw.")

                        self.is_turn = False
                        for row in self.buttons:
                            for button in row:
                                button.setEnabled(False)
                        self.rematch_button.setEnabled(True)
                case "surrender":
                    self.status_label.setText(f"The opponent surrendered. You won!")
                    self.is_turn = False
                    for row in self.buttons:
                        for button in row:
                            button.setEnabled(False)
                    self.rematch_button.setEnabled(True)

    def _rematch(self) -> None:
        """Play another game"""

        self._register()

    def _exit(self) -> None:
        """Exit the game"""

        req = {
            "action": "exit",
            "username": self.username,
            "game_id": self.game_id,
            "chess": self.chess,
        }
        self.client.send_req(req)
        exit(0)
