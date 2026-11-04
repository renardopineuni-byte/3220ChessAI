# Importing Modules
from io import BytesIO
import pygame
import rembg
import requests

'''chess pieces:
2 Kings (B/W)
2 Queens (B/W)
4 Rooks (2B/2W)
4 Bishop (2B/2W)
4 Knight (2B/2W)
16 Pawns (8B/8W)
'''
# initializing pygame module
pygame.init()

# Scaled board dimensions to fit laptop screens with Windows ribbons
sq_size = 60
board_size = sq_size * 8     # 480 px
sidebar_width = 240          # 240 px for move history & forfeit button
width = board_size + sidebar_width  # 720 px total width
height = board_size + 80     # 560 px total height (board + bottom bar)

# Set resizable display surface
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption('Chess Game')

font = pygame.font.SysFont("freesansbold", 16)
medium_font = pygame.font.SysFont("freesansbold", 24)
big_font = pygame.font.SysFont("freesansbold", 26)

timer = pygame.time.Clock()
fps = 60

# game variables and images
white_pieces = [
    'rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn'
]
white_locations = [
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)
]
black_pieces = [
    'rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn'
]
black_locations = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
    (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)
]

captured_pieces_white = []
captured_pieces_black = []

# Move history list and scrolling offset
move_history = []
scroll_offset = 0

# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
turn_step = 0
selection = 100
valid_moves = []

# Scaling piece images to match 60x60 square size
p_size = (50, 50)
p_small_size = (30, 30)

black_queen = pygame.image.load('game/cblackqueen.png')
black_queen = pygame.transform.scale(black_queen, p_size)
black_queen_small = pygame.transform.scale(black_queen, p_small_size)

black_king = pygame.image.load('game/cblackking.png')
black_king = pygame.transform.scale(black_king, p_size)
black_king_small = pygame.transform.scale(black_king, p_small_size)

black_rook = pygame.image.load('game/cblackrook.png')
black_rook = pygame.transform.scale(black_rook, p_size)
black_rook_small = pygame.transform.scale(black_rook, p_small_size)

black_bishop = pygame.image.load('game/cblackbishop.png')
black_bishop = pygame.transform.scale(black_bishop, p_size)
black_bishop_small = pygame.transform.scale(black_bishop, p_small_size)

black_knight = pygame.image.load('game/cblackknight.png')
black_knight = pygame.transform.scale(black_knight, p_size)
black_knight_small = pygame.transform.scale(black_knight, p_small_size)

black_pawn = pygame.image.load('game/cblackpawn.png')
black_pawn = pygame.transform.scale(black_pawn, (42, 42))
black_pawn_small = pygame.transform.scale(black_pawn, p_small_size)

white_queen = pygame.image.load('game/cwhitequeen.png')
white_queen = pygame.transform.scale(white_queen, p_size)
white_queen_small = pygame.transform.scale(white_queen, p_small_size)

white_king = pygame.image.load('game/cwhiteking.png')
white_king = pygame.transform.scale(white_king, p_size)
white_king_small = pygame.transform.scale(white_king, p_small_size)

white_rook = pygame.image.load('game/cwhiterook.png')
white_rook = pygame.transform.scale(white_rook, p_size)
white_rook_small = pygame.transform.scale(white_rook, p_small_size)

white_bishop = pygame.image.load('game/cwhitebishop.png')
white_bishop = pygame.transform.scale(white_bishop, p_size)
white_bishop_small = pygame.transform.scale(white_bishop, p_small_size)

white_knight = pygame.image.load('game/cwhiteknight.png')
white_knight = pygame.transform.scale(white_knight, p_size)
white_knight_small = pygame.transform.scale(white_knight, p_small_size)

white_pawn = pygame.image.load('game/cwhitepawn.png')
white_pawn = pygame.transform.scale(white_pawn, (42, 42))
white_pawn_small = pygame.transform.scale(white_pawn, p_small_size)

white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small, white_rook_small, white_bishop_small]

black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small, black_rook_small, black_bishop_small]

piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

counter = 0
winner = ''
game_over = False

def coord_to_chess(coord):
    """Converts (col, row) tuple into standard chess notation (e.g. (4, 1) -> e2)."""
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    return f"{files[coord[0]]}{ranks[coord[1]]}"

def draw_board():
    # Checkered board
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [board_size - 2 * sq_size - (column * 2 * sq_size), row * sq_size, sq_size, sq_size])
        else:
            pygame.draw.rect(screen, 'light gray', [board_size - sq_size - (column * 2 * sq_size), row * sq_size, sq_size, sq_size])

    # Bottom UI Status Bar
    pygame.draw.rect(screen, 'gray', [0, board_size, width, 80])
    pygame.draw.rect(screen, 'gold', [0, board_size, width, 80], 4)

    # Right Sidebar
    pygame.draw.rect(screen, '#2c2c2c', [board_size, 0, sidebar_width, board_size])
    pygame.draw.rect(screen, 'gold', [board_size, 0, sidebar_width, height], 4)

    status_text = [
        'White: Select Piece',
        'White: Select Target',
        'Black: Select Piece',
        'Black: Select Target'
    ]
    if not game_over:
        screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, board_size + 25))
    else:
        screen.blit(big_font.render(f"GAME OVER - {winner.upper()} WINS!", True, 'red'), (20, board_size + 25))

    # Grid lines
    for j in range(9):
        pygame.draw.line(screen, 'black', (0, sq_size * j), (board_size, sq_size * j), 2)
        pygame.draw.line(screen, 'black', (sq_size * j, 0), (sq_size * j, board_size), 2)

    # Forfeit button inside bottom right of sidebar
    forfeit_rect = [board_size + 20, board_size + 15, sidebar_width - 40, 50]
    pygame.draw.rect(screen, '#b22222', forfeit_rect, border_radius=6)
    screen.blit(medium_font.render('FORFEIT', True, 'white'), (board_size + 65, board_size + 26))

    # Sidebar Header: Move History
    screen.blit(medium_font.render('Move History', True, 'gold'), (board_size + 45, 10))
    pygame.draw.line(screen, 'gold', (board_size + 10, 42), (width - 10, 42), 2)

    # Display Moves with scrolling capability
    start_y = 52 + scroll_offset
    for idx, move in enumerate(move_history):
        y_pos = start_y + (idx * 22)
        if 45 <= y_pos <= board_size - 25:
            txt = font.render(move, True, 'white')
            screen.blit(txt, (board_size + 20, y_pos))

def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        offset = 9 if white_pieces[i] == 'pawn' else 5
        screen.blit(white_images[index], (white_locations[i][0] * sq_size + offset, white_locations[i][1] * sq_size + offset))
        if turn_step < 2 and selection == i:
            pygame.draw.rect(screen, 'red', [white_locations[i][0] * sq_size + 1, white_locations[i][1] * sq_size + 1, sq_size, sq_size], 2)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        offset = 9 if black_pieces[i] == 'pawn' else 5
        screen.blit(black_images[index], (black_locations[i][0] * sq_size + offset, black_locations[i][1] * sq_size + offset))
        if turn_step >= 2 and selection == i:
            pygame.draw.rect(screen, 'blue', [black_locations[i][0] * sq_size + 1, black_locations[i][1] * sq_size + 1, sq_size, sq_size], 2)

def draw_valid(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves:
        pygame.draw.circle(screen, color, (move[0] * sq_size + (sq_size // 2), move[1] * sq_size + (sq_size // 2)), 7)

def check_pawn(location, turn):
    moves_list = []
    if turn == 'white':
        if (location[0], location[1] + 1) not in white_locations and \
           (location[0], location[1] + 1) not in black_locations and location[1] < 7:
            moves_list.append((location[0], location[1] + 1))
            if location[1] == 1 and (location[0], location[1] + 2) not in white_locations and \
               (location[0], location[1] + 2) not in black_locations:
                moves_list.append((location[0], location[1] + 2))
        if (location[0] + 1, location[1] + 1) in black_locations:
            moves_list.append((location[0] + 1, location[1] + 1))
        if (location[0] - 1, location[1] + 1) in black_locations:
            moves_list.append((location[0] - 1, location[1] + 1))
    else:
        if (location[0], location[1] - 1) not in white_locations and (location[0], location[1] - 1) not in black_locations and location[1] > 0:
            moves_list.append((location[0], location[1] - 1))
            if location[1] == 6 and (location[0], location[1] - 2) not in white_locations and (location[0], location[1] - 2) not in black_locations:
                moves_list.append((location[0], location[1] - 2))
        if (location[0] + 1, location[1] - 1) in white_locations:
            moves_list.append((location[0] + 1, location[1] - 1))
        if (location[0] - 1, location[1] - 1) in white_locations:
            moves_list.append((location[0] - 1, location[1] - 1))
    return moves_list

def check_rook(location, turn):
    moves_list = []
    friends = white_locations if turn == 'white' else black_locations
    enemies = black_locations if turn == 'white' else white_locations
    for d in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        chain = 1
        while True:
            target = (location[0] + (chain * d[0]), location[1] + (chain * d[1]))
            if 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                if target not in friends:
                    moves_list.append(target)
                    if target in enemies:
                        break
                    chain += 1
                else:
                    break
            else:
                break
    return moves_list

def check_knight(location, turn):
    moves_list = []
    friends = white_locations if turn == 'white' else black_locations
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for t in targets:
        target = (location[0] + t[0], location[1] + t[1])
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends:
            moves_list.append(target)
    return moves_list

def check_bishop(location, turn):
    moves_list = []
    friends = white_locations if turn == 'white' else black_locations
    enemies = black_locations if turn == 'white' else white_locations
    for d in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        chain = 1
        while True:
            target = (location[0] + (chain * d[0]), location[1] + (chain * d[1]))
            if 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                if target not in friends:
                    moves_list.append(target)
                    if target in enemies:
                        break
                    chain += 1
                else:
                    break
            else:
                break
    return moves_list

def check_queen(location, turn):
    return check_rook(location, turn) + check_bishop(location, turn)

def check_king(location, turn):
    moves_list = []
    friends = white_locations if turn == 'white' else black_locations
    targets = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for t in targets:
        target = (location[0] + t[0], location[1] + t[1])
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends:
            moves_list.append(target)
    return moves_list

def check_options(pieces, locations, turn):
    all_moves_list = []
    for i in range(len(pieces)):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves = check_pawn(location, turn)
        elif piece == 'rook':
            moves = check_rook(location, turn)
        elif piece == 'knight':
            moves = check_knight(location, turn)
        elif piece == 'bishop':
            moves = check_bishop(location, turn)
        elif piece == 'queen':
            moves = check_queen(location, turn)
        elif piece == 'king':
            moves = check_king(location, turn)
        all_moves_list.append(moves)
    return all_moves_list

def game():
    global turn_step, selection, valid_moves, game_over, winner, scroll_offset
    run = True

    white_options = check_options(white_pieces, white_locations, 'white')
    black_options = check_options(black_pieces, black_locations, 'black')

    while run:
        timer.tick(fps)
        screen.fill('dark gray')

        draw_board()
        draw_pieces()
        if selection != 100:
            draw_valid(valid_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Scroll move history using the mouse wheel
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * 20
                if scroll_offset > 0:
                    scroll_offset = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_x, mouse_y = event.pos

                # Check forfeit button click
                if board_size + 20 <= mouse_x <= width - 20 and board_size + 15 <= mouse_y <= board_size + 65:
                    winner = 'black' if turn_step < 2 else 'white'
                    game_over = True
                    continue

                # Ensure click is inside the 8x8 chessboard
                if mouse_x < board_size and mouse_y < board_size:
                    x_coord = mouse_x // sq_size
                    y_coord = mouse_y // sq_size
                    click_coords = (x_coord, y_coord)

                    # White turn
                    if turn_step <= 1:
                        if click_coords in white_locations:
                            selection = white_locations.index(click_coords)
                            turn_step = 1
                            valid_moves = white_options[selection]
                        elif click_coords in valid_moves and selection != 100:
                            origin = white_locations[selection]
                            white_locations[selection] = click_coords
                            move_str = f"{len(move_history)//2 + 1}. W: {coord_to_chess(origin)} -> {coord_to_chess(click_coords)}"

                            if click_coords in black_locations:
                                bp = black_locations.index(click_coords)
                                captured_pieces_white.append(black_pieces[bp])
                                move_str += f" x {black_pieces[bp][:3]}"
                                if black_pieces[bp] == 'king':
                                    winner = 'white'
                                    game_over = True
                                black_pieces.pop(bp)
                                black_locations.pop(bp)

                            move_history.append(move_str)
                            white_options = check_options(white_pieces, white_locations, 'white')
                            black_options = check_options(black_pieces, black_locations, 'black')
                            turn_step = 2
                            selection = 100
                            valid_moves = []

                    # Black turn
                    elif turn_step >= 2:
                        if click_coords in black_locations:
                            selection = black_locations.index(click_coords)
                            turn_step = 3
                            valid_moves = black_options[selection]
                        elif click_coords in valid_moves and selection != 100:
                            origin = black_locations[selection]
                            black_locations[selection] = click_coords
                            move_str = f"{len(move_history)//2 + 1}. B: {coord_to_chess(origin)} -> {coord_to_chess(click_coords)}"

                            if click_coords in white_locations:
                                wp = white_locations.index(click_coords)
                                captured_pieces_black.append(white_pieces[wp])
                                move_str += f" x {white_pieces[wp][:3]}"
                                if white_pieces[wp] == 'king':
                                    winner = 'black'
                                    game_over = True
                                white_pieces.pop(wp)
                                white_locations.pop(wp)

                            move_history.append(move_str)
                            white_options = check_options(white_pieces, white_locations, 'white')
                            black_options = check_options(black_pieces, black_locations, 'black')
                            turn_step = 0
                            selection = 100
                            valid_moves = []

        pygame.display.flip()

    pygame.quit()

game()
