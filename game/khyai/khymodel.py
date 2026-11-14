import chess

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

def eval_strat(board):
  if board.is_checkmate() or board.is_repetition(2):
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