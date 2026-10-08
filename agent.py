import chess


class Agent:
    """Common superclass for every chess agent.

    Each child agent (yours, your partner's) extends this and implements
    choose_move(). Game only ever relies on this interface.
    """

    def __init__(self, name: str = "Agent"):
        self.name = name

    def choose_move(self, board: chess.Board) -> chess.Move:
        """Return a legal move for board.turn. Must not mutate the board."""
        raise NotImplementedError(f"{type(self).__name__} must implement choose_move()")

    def __str__(self) -> str:
        return self.name
