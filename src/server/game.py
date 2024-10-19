import uuid


class Game:
    def __init__(self, player_x: str, player_o: str) -> None:
        self.id = str(uuid.uuid4())
        self.chess_player = {"X": None, "O": None}
        self.board = [" " for _ in range(9)]
        self.current_turn = "X"
        self.is_end = False
        self.winner = None

        self._set_players(player_x=player_x, player_o=player_o)

    def _set_players(self, player_x: str, player_o: str) -> None:
        # TODO: add pseudorandomness
        self.chess_player["X"] = player_x
        self.chess_player["O"] = player_o

    def move(self, x: int, y: int, chess: str) -> None:
        """Make a move on the board

        Args:
            x (int): index of the row
            y (int): index of the column
            chess (str): "X" or "O"
        """
        
        self.board[x * 3 + y] = chess
        self._check_board()
        self.current_turn = "O" if chess == "X" else "X"

    def _check_board(self) -> None:
        """Check if there is a winner or a draw"""

        win_conditions = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),  # rows
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),  # columns
            (0, 4, 8),
            (2, 4, 6),  # diagonals
        ]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.winner = self.board[a]
                self.is_end = True
                return
        # Check for a draw
        if all(cell != " " for cell in self.board):
            self.is_end = True
            self.winner = False
