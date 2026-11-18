import chess
from agent import Agent

'''
Strategy: 
Surround the enemy King
Attack the enemy king


look at the board, evaluate whites moves along with the given strategy, return a score, positive means white is doing good, negative means black is doing good

Pawn = 1, Knight = 3, Bishop = 3, Rook = 5, Queen = 9 x100

Locate enemy king, for each square around the king is attacking or threatening it, +score 
For each pawn on the enemy side of the board +score
if enemy king is in check ++score
if enemy queen or rook is threatened +score
'''

piece_vals={
  chess.PAWN: 100,
  chess.KNIGHT:300,
  chess.BISHOP:300,
  chess.ROOK:500,
  chess.QUEEN:900,
  chess.KING:0}

KING_ZONE = 150
PAWN_MOVE = 100
KING_CHECK = 500
PIECE_THREAT = 250

board = chess.Board()

def eval_strat(board: chess.Board) -> float:
  if board.is_checkmate() or board.is_repetition(5):
    if board.turn == chess.WHITE:
      return -99999
    else:
      return 99999
  if board.is_stalemate():
    return 0
  
  white_score, black_score = 0, 0
  
  
  white_king_location = board.king(chess.WHITE) 
  black_king_location = board.king(chess.BLACK)
  #give the squares around the king

  wk_area = board.attacks(white_king_location) #Gets the set of attacked squares from the given square.
  bk_area = board.attacks(black_king_location) 

  
  for square in chess.SQUARES:
    piece = board.piece_at(square)
    if piece is None:
      continue
    baseval = piece_vals[piece.piece_type]
    bonus = 0
    
    #For each pawn on the enemy side of the board +score
    if piece.piece_type is chess.PAWN:
      rank = chess.square_rank(square)
      #white starts at 2 and moves up, black starts at 7 and moves down
      if piece.color == chess.WHITE:
        ranks_moved = (rank-2)
      else:
        ranks_moved = ( 7-rank)
      bonus += ranks_moved * PAWN_MOVE
      
    attacked = board.attacks(square)
    if piece.color == chess.WHITE:
      area_attacks = 0 
      for sq in attacked:
        if sq in bk_area:
          area_attacks +=1
      bonus+= (area_attacks*KING_ZONE)
    else:
      area_attacks = 0 
      for sq in attacked:
        if sq in wk_area:
          area_attacks +=1
      bonus+= (area_attacks*KING_ZONE)      
      
    for targetsq in attacked:
      target = board.piece_at(targetsq)
      if target is not None and target.color != piece.color:
        if target.piece_type in (chess.QUEEN, chess.ROOK):
          bonus += PIECE_THREAT
          
    #theres an error where the rook keeps moving to the same spots so this rewards it moving from thr same rank
    if piece.piece_type in (chess.KNIGHT, chess.BISHOP):
      rank = chess.square_rank(square)
      if piece.color ==chess.WHITE and rank > 0:
        bonus += 50
      elif piece.color == chess.BLACK and rank < 7:
        bonus += 50
          
    if piece.color ==chess.WHITE:
      white_score +=baseval+bonus
    else:
      black_score+=baseval+bonus
      
    if board.is_check():
      if board.turn ==chess.BLACK:
        white_score += KING_CHECK
      else:
        black_score += KING_CHECK
        
    return white_score - black_score
  
def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maxplayer: bool):
  #base case if game over 
  if depth == 0 or board.is_game_over():
    return eval_strat(board), None
      
  bestmove= None
  ordered_moves = sorted(
        board.legal_moves,
        key=lambda m: (board.is_capture(m), board.gives_check(m)),
        reverse=True
    )
  
  if maxplayer:
    maxeval= float('-inf')#infinity
    
    for move in ordered_moves:
      board.push(move)
      evalscore, _ = minimax(board, depth-1, alpha, beta, False)
      board.pop()
    
      if evalscore > maxeval: #if its greater than neg inf
        maxeval = evalscore
        best_move = move
      alpha = max(alpha, evalscore)
      if beta <= alpha:
        break  #beta cutoff -- the MIN ancestor will simply never choose the path leading to this node because it already has a better (lower) option
    return maxeval, best_move
  else:
    mineval = float('inf')
    for move in ordered_moves:
      board.push(move)
      eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
      board.pop()

      if eval_score < mineval:
        mineval = eval_score
        best_move = move
        beta = min(beta, eval_score)
        if beta <= alpha:
          break  #alpha cutoff
    return mineval, best_move

class kingAgent(Agent):
  def __init__(self, name: str = "King", depth: int = 3):
    super().__init__(name)
    self.depth = depth

  def choose_move(self, board: chess.Board) -> chess.Move:
    is_white = (board.turn == chess.WHITE)
    _, best_move = minimax(board,
      depth=self.depth,
      alpha=float('-inf'),
      beta=float('inf'),
      maxplayer=is_white)

      #Fallback
    if best_move is None:
      return next(iter(board.legal_moves))
    return best_move
