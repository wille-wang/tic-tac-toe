import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt


class Board(QMainWindow):
    """GUI for the Tic-Tac-Toe game"""

    def __init__(self, username):
        super().__init__()
        # game information
        self.username = username
        self.reset_board()
        self.game_id = None
        self.chess = None  # X or O

    def reset_board(self):
        """reset the board to the initial state"""
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
                self.layout.addWidget(button, i + 1, j)
                row.append(button)
            self.buttons.append(row)

    def make_move(self, x, y):
        # Placeholder for move logic
        pass
