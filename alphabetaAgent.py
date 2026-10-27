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

class AlphaBetaAgent(Agent):
    """Fixed-depth minimax with alpha-beta pruning, using Agent.evaluate.

    White maximises the score, Black minimises it. Returns the same score as
    plain minimax at the same depth, but visits far fewer positions.
    """

    def __init__(self, name: str = "AlphaBeta", depth: int = 5):
        super().__init__(name)
        self.depth = depth
        self.nodes_searched = 0

    def choose_move(self, board: chess.Board) -> chess.Move:
        self.nodes_searched = 0
        maximising = board.turn == chess.WHITE
        best_score = float("-inf") if maximising else float("inf")
        best_moves = []

        for move in self._ordered_moves(board):
            board.push(move)
            # Scores are integers, so widening the window by 1 keeps moves that
            # TIE the best score exact (needed for the random tie-break) while
            # still pruning anything strictly worse.
            if maximising:
                score = self._alphabeta(board, self.depth - 1, best_score - 1, float("inf"))
            else:
                score = self._alphabeta(board, self.depth - 1, float("-inf"), best_score + 1)
            board.pop()

            if (maximising and score > best_score) or (not maximising and score < best_score):
                best_score, best_moves = score, [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves)

    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        self.nodes_searched += 1

        if board.is_game_over():
            return self._terminal_score(board, depth)
        if depth == 0:
            return self.evaluate(board)

        if board.turn == chess.WHITE:
            value = float("-inf")
            for move in self._ordered_moves(board):
                board.push(move)
                value = max(value, self._alphabeta(board, depth - 1, alpha, beta))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:  # Black would never allow this line
                    break
        else:
            value = float("inf")
            for move in self._ordered_moves(board):
                board.push(move)
                value = min(value, self._alphabeta(board, depth - 1, alpha, beta))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:  # White would never allow this line
                    break
        return value

    @staticmethod
    def _ordered_moves(board: chess.Board):
        """Captures first: good moves early means more cutoffs."""
        return sorted(board.legal_moves, key=board.is_capture, reverse=True)

    @staticmethod
    def _terminal_score(board: chess.Board, depth: int) -> float:
        if board.is_checkmate():
            bonus = MATE_SCORE + depth  # faster mate = better
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
