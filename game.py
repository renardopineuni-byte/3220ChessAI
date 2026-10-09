import chess

from agent import Agent


class Game:
    def __init__(self, white: Agent, black: Agent, fen: str = None):
        self.board = chess.Board(fen) if fen else chess.Board()
        self.agents = {chess.WHITE: white, chess.BLACK: black}
        self.move_history = []  # list of chess.Move
        self.san_history = []   # matching SAN strings, e.g. 'Nf3'
        self.last_san = None

    @property
    def current_agent(self) -> Agent:
        return self.agents[self.board.turn]

    def is_over(self) -> bool:
        return self.board.is_game_over()

    def step(self) -> chess.Move:
        """Ask the agent to move, validate its move, play it, and return it."""
        if self.is_over():
            raise RuntimeError("Game is already over")

        agent = self.current_agent
        # Give the agent a copy so it can't corrupt the real board
        move = agent.choose_move(self.board.copy())

        if move not in self.board.legal_moves:
            raise ValueError(f"{agent.name} returned illegal move: {move}")

        # SAN depends on the position, so it must be computed BEFORE pushing
        self.last_san = self.board.san(move)
        self.board.push(move)
        self.move_history.append(move)
        self.san_history.append(self.last_san)
        return move

    def play(self, verbose: bool = False, max_moves: int = 100) -> str:
        """Run until the game ends. Returns the result string, e.g. '1-0'."""
        while not self.is_over() and len(self.move_history) < max_moves:
            mover = self.current_agent.name
            move = self.step()
            if verbose:
                print(f"{mover}: {self.last_san}")
        return self.board.result(claim_draw=True)


def render_board(board: chess.Board, white_at_bottom: bool = True) -> str:
    """ASCII board with coordinates. Flipped when white_at_bottom is False."""
    ranks = range(7, -1, -1) if white_at_bottom else range(8)
    files = range(8) if white_at_bottom else range(7, -1, -1)
    lines = []
    for r in ranks:
        row = []
        for f in files:
            piece = board.piece_at(chess.square(f, r))
            row.append(piece.symbol() if piece else ".")
        lines.append(f"{r + 1}  " + " ".join(row))
    lines.append("")
    lines.append("   " + " ".join(chess.FILE_NAMES[f] for f in files))
    return "\n".join(lines)


def choose_mode() -> str:
    while True:
        print("1) Human vs AI")
        print("2) AI vs AI")
        choice = input("Select mode: ").strip()
        if choice in ("1", "2"):
            return choice
        print("Please enter 1 or 2.")


def choose_colour() -> bool:
    """Returns True if the human plays White."""
    while True:
        choice = input("Play as (w)hite or (b)lack? ").strip().lower()
        if choice in ("w", "white"):
            return True
        if choice in ("b", "black"):
            return False
        print("Please enter w or b.")


def run_cli():
    # Swap RandomAgent for the real child agents once they're written
    from randomAgent import RandomAgent
    from humanAgent import HumanAgent
    from sniperAgent import SniperAgent

    if choose_mode() == "1":
        human_is_white = choose_colour()
        human, ai = HumanAgent("You"), SniperAgent("AI")
        game = Game(human, ai) if human_is_white else Game(ai, human)
        print("\nType moves like 'e4', 'Nf3' or 'g1f3'. Type 'quit' to exit.\n")
        print(render_board(game.board, human_is_white), "\n")
        while not game.is_over():
            mover = game.current_agent
            move = game.step()
            if mover is ai:
                print(f"{ai.name} plays {move.uci()}")
            print(render_board(game.board, human_is_white), "\n")
        print("Result:", game.board.result(claim_draw=True))
    else:
        game = Game(SniperAgent("White"), RandomAgent("Black"))
        result = game.play(verbose=True)
        print(render_board(game.board))
        print("Result:", result)

if __name__ == "__main__":
    run_cli()