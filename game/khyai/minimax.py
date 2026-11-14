import chess
import numpy as np
from khyai.khymodel import eval_strat


board = chess.Board()
'''score is sum of while - sum of black, 
white is max, black is min
pawn=1, knight=3, bishop=3, rook=5, queen=9, king=0 
'''
piece_vals={
  chess.PAWN: 1,
  chess.KNIGHT:3,
  chess.BISHOP:3,
  chess.ROOK:5,
  chess.QUEEN:9,
  #king doesnt have a value but idk if i should just give it a really big value because its like gameending yk... tbd
  chess.KING:0}
'''
def evalboard(board):
  if board.is_checkmate():
    if board.turn == chess.WHITE:
      return -99999
    else:
      return 99999
  if board.is_stalemate():
    return 0
  
  score =0
  for square in chess.SQUARES:
    piece=board.piece_at(square)
    if piece:
      val = piece_vals[piece.piece_type]
      if piece.color == chess.WHITE:
        score += val
      else:
        score -= val
  return score
  
'''

def minimax(board, depth, alpha, beta, maxplayer, eval=eval_strat):
  #base case if game over 
  if depth == 0 or board.is_game_over():
    return eval(board), None
      
  bestmove= None
  
  if maxplayer:
    maxeval= float('-inf')#infinity
    
    for move in board.legal_moves:
      board.push(move)
      evalscore, _ = minimax(board, depth-1, alpha, beta, False)
      board.pop()#undo move
    
      if evalscore > maxeval: #if its greater than neg inf
        maxeval = evalscore
        best_move = move
      alpha = max(alpha, evalscore)
      if beta <= alpha:
        break  #beta cutoff -- the MIN ancestor will simply never choose the path leading to this node because it already has a better (lower) option
    return maxeval, best_move
  else:
    mineval = float('inf')
    for move in board.legal_moves:
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
          
          
