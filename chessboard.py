#gui of the project
import os
import threading
import pygame
import chess

from game import Game
from humanAgent import HumanAgent
from sniperAgent import SniperAgent
from kingAgent import kingAgent

# ---------------------------------------------------------------- constants
SQ = 60                       # square size in px
BOARD = SQ * 8                # 480
SIDEBAR = 240
BAR = 80                      # bottom status bar height
W, H = BOARD + SIDEBAR, BOARD + BAR
FPS = 60
AI_DELAY_MS = 400             # pause between moves in AI vs AI so it's watchable

LIGHT = (222, 222, 222)
DARK = (150, 150, 150)

#file path of piece pictures
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game")
PIECE_NAMES = {chess.PAWN: "pawn", chess.ROOK: "rook", chess.KNIGHT: "knight",
            chess.BISHOP: "bishop", chess.QUEEN: "queen", chess.KING: "king"}

# Agents the human can pick from. Add new agents here.
AGENT_FACTORIES = {
    "Sniper": lambda: SniperAgent("Sniper"),
    "King": lambda: kingAgent("King", depth=3),
}

MENU_RECT = pygame.Rect(BOARD + 10, BOARD + 15, 105, 50)
ACTION_RECT = pygame.Rect(BOARD + 125, BOARD + 15, 105, 50)


# ------------------------------------------------------- board orientation
def sq_to_xy(sq, white_bottom):
    """Top-left pixel of a square. Flips both axes when Black is at the bottom."""
    f, r = chess.square_file(sq), chess.square_rank(sq)
    col = f if white_bottom else 7 - f
    row = 7 - r if white_bottom else r
    return col * SQ, row * SQ


def xy_to_sq(x, y, white_bottom):
    """Inverse of sq_to_xy: pixel position -> chess square."""
    col, row = x // SQ, y // SQ
    f = col if white_bottom else 7 - col
    r = 7 - row if white_bottom else row
    return chess.square(f, r)


def load_images():
    """Load piece sprites keyed by (colour, piece_type). Missing files -> None
    (a letter is drawn instead so the game is still playable)."""
    images = {}
    for colour, cname in ((chess.WHITE, "white"), (chess.BLACK, "black")):
        for pt, name in PIECE_NAMES.items():
            path = os.path.join(ASSET_DIR, f"c{cname}{name}.png")
            try:
                img = pygame.image.load(path)
                size = (42, 42) if pt == chess.PAWN else (50, 50)
                images[(colour, pt)] = pygame.transform.scale(img, size)
            except (pygame.error, FileNotFoundError):
                images[(colour, pt)] = None
    return images


#actual game processing
class Session:

    def __init__(self, game: Game, human_colour):
        self.game = game
        self.human_colour = human_colour          # chess.WHITE / BLACK / None (AI vs AI)
        self.white_bottom = human_colour != chess.BLACK
        self.selected = None                      # selected square (human)
        self.targets = []                         # legal destination squares
        self.thinking = False                     # AI worker thread running?
        self.pending = None                       # (move, error) from worker thread
        self.over_text = None
        self.paused = False
        self.step_once = False
        self.next_ai_at = 0
        self.scroll = 0                           # history scroll (lines from the end)


    def is_human_turn(self):
        return self.human_colour is not None and self.game.board.turn == self.human_colour

    def clear_selection(self):
        self.selected, self.targets = None, []

    def finish_if_over(self):
        board = self.game.board
        if board.is_game_over(claim_draw=True):
            outcome = board.outcome(claim_draw=True)
            reason = outcome.termination.name.replace("_", " ").title()
            if outcome.winner is None:
                self.over_text = f"Draw - {reason}"
            else:
                side = "White" if outcome.winner == chess.WHITE else "Black"
                self.over_text = f"{reason} - {side} wins"
            return True
        return False

    def forfeit(self):
        if self.over_text or self.human_colour is None:
            return
        winner = "Black" if self.human_colour == chess.WHITE else "White"
        self.over_text = f"You forfeited - {winner} wins"

    # AI runs in a thread so the window never freezes while searching
    def start_ai(self):
        self.thinking = True
        agent = self.game.current_agent
        board_copy = self.game.board.copy()

        def work():
            try:
                self.pending = (agent.choose_move(board_copy), None)
            except Exception as exc:  # report agent bugs in the GUI
                self.pending = (None, str(exc))

        threading.Thread(target=work, daemon=True).start()

    def update(self, now):
        """Called once per frame: collect AI moves, start new searches."""
        if self.over_text:
            return

        if self.pending is not None:
            move, err = self.pending
            self.pending, self.thinking = None, False
            if err:
                self.over_text = f"Agent error: {err}"
                print(f"Agent error: {err}")
                return
            try:
                self.game.apply_move(move, self.game.current_agent.name)
            except ValueError as exc:
                self.over_text = str(exc)
                return
            self.next_ai_at = now + AI_DELAY_MS
            self.scroll = 0

        if self.finish_if_over() or self.thinking or self.is_human_turn():
            return

        # AI vs AI can be paused; stepping allows exactly one move while paused
        if self.human_colour is None and self.paused and not self.step_once:
            return
        if now >= self.next_ai_at:
            self.step_once = False
            self.start_ai()

    # human input
    def click_board(self, pos):
        if self.over_text or self.thinking or not self.is_human_turn():
            return
        board = self.game.board
        sq = xy_to_sq(pos[0], pos[1], self.white_bottom)

        if self.selected is not None and sq in self.targets:
            move = chess.Move(self.selected, sq)
            if move not in board.legal_moves:      # must be a promotion (auto-queen)
                move = chess.Move(self.selected, sq, promotion=chess.QUEEN)
            self.game.apply_move(move, "You")
            self.clear_selection()
            self.scroll = 0
            self.next_ai_at = pygame.time.get_ticks() + 150
            return

        piece = board.piece_at(sq)
        if piece and piece.color == board.turn:
            self.selected = sq
            self.targets = [m.to_square for m in board.legal_moves if m.from_square == sq]
        else:
            self.clear_selection()


#rendering logic
def draw_game(screen, s, fonts, images):
    screen.fill((169, 169, 169))
    board = s.game.board
    wb = s.white_bottom

    # squares
    for sq in chess.SQUARES:
        x, y = sq_to_xy(sq, wb)
        light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
        pygame.draw.rect(screen, LIGHT if light else DARK, (x, y, SQ, SQ))

    # last-move highlight
    if s.game.move_history:
        hl = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
        hl.fill((255, 215, 0, 90))
        last = s.game.move_history[-1]
        for sq in (last.from_square, last.to_square):
            screen.blit(hl, sq_to_xy(sq, wb))

    # coordinate labels (they flip with the board)
    for i in range(8):
        f = i if wb else 7 - i
        screen.blit(fonts["small"].render(chess.FILE_NAMES[f], True, "black"),
                    (i * SQ + SQ - 10, BOARD - 14))
        r = 7 - i if wb else i
        screen.blit(fonts["small"].render(str(r + 1), True, "black"), (3, i * SQ + 2))

    # grid lines
    for j in range(9):
        pygame.draw.line(screen, "black", (0, SQ * j), (BOARD, SQ * j), 2)
        pygame.draw.line(screen, "black", (SQ * j, 0), (SQ * j, BOARD), 2)

    # pieces
    for sq, piece in board.piece_map().items():
        x, y = sq_to_xy(sq, wb)
        img = images[(piece.color, piece.piece_type)]
        if img:
            off = (SQ - img.get_width()) // 2
            screen.blit(img, (x + off, y + off))
        else:
            col = "white" if piece.color == chess.WHITE else "black"
            txt = fonts["big"].render(piece.symbol().upper(), True, col)
            screen.blit(txt, txt.get_rect(center=(x + SQ // 2, y + SQ // 2)))

    # selection + legal targets
    if s.selected is not None:
        colour = "red" if board.turn == chess.WHITE else "blue"
        x, y = sq_to_xy(s.selected, wb)
        pygame.draw.rect(screen, colour, (x + 1, y + 1, SQ, SQ), 3)
        for t in s.targets:
            tx, ty = sq_to_xy(t, wb)
            pygame.draw.circle(screen, colour, (tx + SQ // 2, ty + SQ // 2), 7)

    # bottom bar
    pygame.draw.rect(screen, "gray", (0, BOARD, W, BAR))
    pygame.draw.rect(screen, "gold", (0, BOARD, W, BAR), 4)
    screen.blit(fonts["big"].render(status_text(s), True, "black"), (20, BOARD + 28))

    # sidebar
    pygame.draw.rect(screen, "#2c2c2c", (BOARD, 0, SIDEBAR, BOARD))
    pygame.draw.rect(screen, "gold", (BOARD, 0, SIDEBAR, H), 4)
    screen.blit(fonts["med"].render("Move History", True, "gold"), (BOARD + 45, 10))
    pygame.draw.line(screen, "gold", (BOARD + 10, 42), (W - 10, 42), 2)

    san = s.game.san_history
    lines = [f"{i // 2 + 1}. " + "  ".join(san[i:i + 2]) for i in range(0, len(san), 2)]
    rows = (BOARD - 60) // 22
    max_scroll = max(0, len(lines) - rows)
    s.scroll = max(0, min(s.scroll, max_scroll))
    start = max_scroll - s.scroll
    for n, line in enumerate(lines[start:start + rows]):
        screen.blit(fonts["small"].render(line, True, "white"), (BOARD + 20, 52 + n * 22))

    # buttons
    draw_button(screen, fonts, MENU_RECT, "MENU", "#444444")
    if s.human_colour is not None:
        if not s.over_text:
            draw_button(screen, fonts, ACTION_RECT, "FORFEIT", "#b22222")
    else:
        draw_button(screen, fonts, ACTION_RECT, "RESUME" if s.paused else "PAUSE", "#2e6b2e")


def status_text(s):
    if s.over_text:
        return s.over_text
    board = s.game.board
    side = "White" if board.turn == chess.WHITE else "Black"
    if s.thinking:
        return f"{s.game.current_agent.name} ({side}) is thinking..."
    if s.is_human_turn():
        return f"Your move ({side})"
    if s.human_colour is None and s.paused:
        return "Paused - SPACE resume, N step"
    return f"{side} to move"


def draw_button(screen, fonts, rect, label, colour):
    pygame.draw.rect(screen, colour, rect, border_radius=6)
    txt = fonts["med"].render(label, True, "white")
    screen.blit(txt, txt.get_rect(center=rect.center))


#  menus
def menu_layout(state):
    """Return (title, [(label, value), ...]) for a menu state."""
    if state == "mode":
        return "Chess AI", [("Human vs AI", "human"), ("AI vs AI", "ai"), ("Quit", "quit")]
    if state == "colour":
        return "Play as...", [("White", "white"), ("Black", "black"), ("Back", "back")]
    # state == "agent"
    items = [(name, name) for name in AGENT_FACTORIES] + [("Back", "back")]
    return "Choose your opponent", items


def menu_rects(items):
    rects = []
    y = 190
    for _ in items:
        rects.append(pygame.Rect(W // 2 - 130, y, 260, 54))
        y += 70
    return rects


def draw_menu(screen, fonts, state):
    screen.fill("#2c2c2c")
    title, items = menu_layout(state)
    t = fonts["title"].render(title, True, "gold")
    screen.blit(t, t.get_rect(center=(W // 2, 110)))
    for rect, (label, _) in zip(menu_rects(items), items):
        draw_button(screen, fonts, rect, label, "#444444")


def new_session(mode, colour=None, agent_name=None):
    if mode == "human":
        human, ai = HumanAgent("You"), AGENT_FACTORIES[agent_name]()
        human_colour = chess.WHITE if colour == "white" else chess.BLACK
        game = Game(human, ai) if human_colour == chess.WHITE else Game(ai, human)
        return Session(game, human_colour)
    # AI vs AI: the pair's two agents face each other
    names = list(AGENT_FACTORIES)
    # runs the game with the 2 AIs. Use Index 0 for Sniper and index 1 for Khy.
    #print(AGENT_FACTORIES[names[1]])
    game = Game(AGENT_FACTORIES[names[0]](), AGENT_FACTORIES[names[1]]())
    return Session(game, None)


# --------------------------------------------------------------------- main
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Chess")
    fonts = {
        "small": pygame.font.SysFont("freesansbold", 16),
        "med": pygame.font.SysFont("freesansbold", 24),
        "big": pygame.font.SysFont("freesansbold", 26),
        "title": pygame.font.SysFont("freesansbold", 48),
    }
    images = load_images()
    clock = pygame.time.Clock()

    state = "mode"        # mode -> colour -> agent -> playing
    chosen_colour = None
    session = None
    running = True

    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif state == "playing":
                if event.type == pygame.MOUSEWHEEL:
                    session.scroll += event.y * 2
                elif event.type == pygame.KEYDOWN and session.human_colour is None:
                    if event.key == pygame.K_SPACE:
                        session.paused = not session.paused
                    elif event.key == pygame.K_n:
                        session.paused, session.step_once = True, True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if MENU_RECT.collidepoint(event.pos):
                        state, session = "mode", None   # abandon game, back to menu
                        break
                    elif ACTION_RECT.collidepoint(event.pos):
                        if session.human_colour is None:
                            session.paused = not session.paused
                        else:
                            session.forfeit()
                    elif event.pos[0] < BOARD and event.pos[1] < BOARD:
                        session.click_board(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                _, items = menu_layout(state)
                for rect, (_, value) in zip(menu_rects(items), items):
                    if not rect.collidepoint(event.pos):
                        continue
                    if state == "mode":
                        if value == "human":
                            state = "colour"
                        elif value == "quit":
                            running = False
                        else:
                            session, state = new_session("ai"), "playing"
                    elif state == "colour":
                        if value == "back":
                            state = "mode"
                        else:
                            chosen_colour, state = value, "agent"
                    elif state == "agent":
                        if value == "back":
                            state = "colour"
                        else:
                            session = new_session("human", chosen_colour, value)
                            state = "playing"
                    break

        if state == "playing":
            session.update(now)
            draw_game(screen, session, fonts, images)
        else:
            draw_menu(screen, fonts, state)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

