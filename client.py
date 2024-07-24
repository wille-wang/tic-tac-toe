import sys
import argparse
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
        self.player = None  # X or O

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

if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # start the GUI application
    app = QApplication(sys.argv)
    client = TicTacToeClient(args.username, args.host, args.port)
    client.show()
    sys.exit(app.exec_())