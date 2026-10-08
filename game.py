import chess

from agent import Agent

class Game:
    def __init__(self, white: Agent, black: Agent, fen: str = None):
        self.board = chess.Board(fen) if fen else chess.Board()
        self.agents = {chess.WHITE: white, chess.BLACK: black}
        self.move_history = []  # list of chess.Move

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

        self.board.push(move)
        self.move_history.append(move)
        return move

    def play(self, verbose: bool = False, max_moves: int = 500) -> str:
        """Run until the game ends. Returns the result string, e.g. '1-0'."""
        while not self.is_over() and len(self.move_history) < max_moves:
            mover = self.current_agent.name
            move = self.step()
            if verbose:
                print(f"{mover}: {move.uci()}")
        return self.board.result(claim_draw=True)


if __name__ == "__main__":
    # Swap these for the two real child agents once they're written
    from randomAgent import RandomAgent

    game = Game(RandomAgent("White"), RandomAgent("Black"))
    result = game.play(verbose=True)
    print(game.board)
    print("Result:", result)
