import random
import chess

from agent import Agent


class RandomAgent(Agent):
    """Throwaway agent for testing Game before the real agents exist."""

    def __init__(self, name: str = "Random"):
        super().__init__(name)

    def choose_move(self, board: chess.Board) -> chess.Move:
        return random.choice(list(board.legal_moves))