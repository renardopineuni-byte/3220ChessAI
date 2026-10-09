import random
import chess

from agent import Agent

MATE_SCORE = 10_000

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

class SniperAgent(Agent):
    """Plain fixed-depth minimax using Agent.evaluate (White minus Black material).

    White maximises the score, Black minimises it.
    """

    def __init__(self, name: str = "Minimax", depth: int = 3):
        super().__init__(name)
        self.depth = depth
        self.nodes_searched = 0  # handy for comparing against alpha-beta later

    def choose_move(self, board: chess.Board) -> chess.Move:
        self.nodes_searched = 0
        maximising = board.turn == chess.WHITE
        best_score = float("-inf") if maximising else float("inf")
        best_moves = []

        for move in board.legal_moves:
            board.push(move)
            score = self._minimax(board, self.depth - 1)
            board.pop()

            if (maximising and score > best_score) or (not maximising and score < best_score):
                best_score, best_moves = score, [move]
            elif score == best_score:
                best_moves.append(move)

        # Random tie-break so equal moves don't make every game identical
        return random.choice(best_moves)

    def _minimax(self, board: chess.Board, depth: int) -> float:
        self.nodes_searched += 1

        if board.is_game_over():
            return self._terminal_score(board, depth)
        if depth == 0:
            return self.evaluate(board)

        if board.turn == chess.WHITE:
            best = float("-inf")
            for move in board.legal_moves:
                board.push(move)
                best = max(best, self._minimax(board, depth - 1))
                board.pop()
        else:
            best = float("inf")
            for move in board.legal_moves:
                board.push(move)
                best = min(best, self._minimax(board, depth - 1))
                board.pop()
        return best

    @staticmethod
    def _terminal_score(board: chess.Board, depth: int) -> float:
        if board.is_checkmate():
            # Side to move has been mated. Extra depth left = mate found sooner = better.
            bonus = MATE_SCORE + depth
            return -bonus if board.turn == chess.WHITE else bonus
        return 0  # stalemate, insufficient material, etc.

    def evaluate(self, board: chess.Board) -> int:
        """Material score: White's points minus Black's points.

        Positive means White is ahead, negative means Black is ahead.
        """
        score = 0
        for piece_type, value in PIECE_VALUES.items():
            score += value * len(board.pieces(piece_type, chess.WHITE))
            score -= value * len(board.pieces(piece_type, chess.BLACK))
        return score

