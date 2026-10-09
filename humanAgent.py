import chess

from agent import Agent


class HumanAgent(Agent):
    """Reads a move from the console. Accepts SAN (Nf3, e4, O-O) or UCI (g1f3)."""

    def __init__(self, name: str = "Human"):
        super().__init__(name)

    def choose_move(self, board: chess.Board) -> chess.Move:
        side = "White" if board.turn == chess.WHITE else "Black"
        while True:
            text = input(f"{self.name} ({side}) move: ").strip()
            if text.lower() in ("quit", "exit"):
                raise SystemExit("Game aborted by player.")
            move = self._parse(board, text)
            if move is not None:
                return move
            print(f"  '{text}' is not a legal move here. Try e.g. 'e4', 'Nf3' or 'g1f3'.")

    @staticmethod
    def _parse(board: chess.Board, text: str):
        for parser in (board.parse_san, board.parse_uci):
            try:
                return parser(text)
            except ValueError:  # covers illegal, ambiguous and invalid moves
                continue
        return None