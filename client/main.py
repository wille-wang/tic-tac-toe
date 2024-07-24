import sys
import argparse
from PySide6.QtWidgets import QApplication
from board import Board
from client import Client

if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=44444)
    args = parser.parse_args()

    # start the GUI application
    app = QApplication(sys.argv)
    board = Board(username=args.username)
    board.show()

    # start the client and pass the board instance to it
    client = Client(
        host=args.host, port=args.port, username=args.username, board=board
    )

    sys.exit(app.exec())
