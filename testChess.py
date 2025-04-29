#errors to fix:
    #FIXED: If white pawn taken, position_dict not updated for removal. Causes problems when another piece wants to move to that position.
    #FIXED: Castling, position_dict not updated for moving the rook. Causes problems with the rook moving the rook. 
        #note: These scenarios are similar, in that all_moves is updated correctly, but position_dict is not. So it looks right, but it is not.
    #FIXED: Pawn capturing on last row not working. This is because there are multiple notations for promotion of a pawn, eg; 'f7g8r', 'f7g8q', 'f7g8b'
    #FIXED scenario: en passant: different + or - 1 for if it is black or white capturing
    #FIXED: Pawn updated as 'Piece.white_PAWN5': '8q'. Need to update promoted pawns
    #FIXED: if loading in the moves before starting, the promoted pawns are not updated. 
    #FIXED: do_temp_capture trying to fix pinned queens scenario
    #FIXED: get_legal_capture_moves_pawns, not working for some reason
    #FIXED: pinned queens moves_string, doing queen to e5 says it puts black king in check
    #FIXED: Notify when the king is in check 
    #FIXED: if king is in check by pawn promotion, not shown as check.
    #FIXED: Promoted pawns in legal moves
    #FIXED: Print the board, without stockfish!
    #FIXED: Castling command takes forever to load (was still using stockfish)
    #FIXED: black always stays during a capture??
    #FIXED: Asks for pawn promotion piece, before checks if legal
    #FIXED: Notify when the game is over, either by checkmate or stalemate
    #FIXED: If more than one piece can move to the same square, we present an error, but there is no way of fixing it
    #FIXED: If king moves to a square it can't, but it woucld be in check in that square, it shows as check error message
    #FIXED: If there are multiple moves to be checked, (piece moves) and none of them are legal, the error message is generic instead of specific check message
    #FIXED: when doing the "undo" intention, board positions list is acting weird. stalemate isn't working properly
    #FIXED: add 50 move draw
    #FIXED: undo or restart, doesn't update 50 move draw variables
    #FIXED: add insufficient material draw. currently working on: check_for_insufficient_material_draw()
    #FIXED: make phoenix class have the generation of possible moves logic
    #FIXED: The problem with the en passant load and the pawn promotion load was that I was passing in all the moves at once, instead of adding them one at a time (7, 8, 9, 12, 23)
    #FIXED: 33, added 50_move_count in play loop
    #FIXED: #TODO 47, 28 -> I think it is working now, but I might need to check up on it more later
    #FIXED: Pieces that can move to the same square doesn't work if it is on the last row. (40, 42, 43, 44)
    #FIXED: Generate move tree

    #scenario: pawns that aren't allowed to move 2 forward are now allowed to
    #scenario: evaluate each position in the tree, and apply alpha beta to go faster and deeper
    #scenario: Work with other commands, like take over, restart, undo, etc;
    #scenario: can't undo a checkmate or stalemate

import re
import os
from collections import Counter
from PHOENIX import Phoenix
phoenix = Phoenix()

def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS/Linux
        os.system('clear')

#1 first move
# moves_string = ['e2e4']

#2 second move
# moves_string = ['e2e4', 'd7d5']

#3 third move
# moves_string = ['e2e4', 'd7d5', 'e4d5']

#4 pinned queens
# moves_string = ['e2e4', 'f7f5', 'd2d3', 'f5e4', 'd1e2', 'e4d3', 'c2d3', 'e7e5', 'd3d4', 'd8e7', 'e2e5']

#5 pinned en passant
# moves_string = ['e2e4', 'e7e6', 'f2f4', 'd8e7', 'f4f5', 'e6f5', 'e4e5', 'd7d5']

#6 en passant legal on one side but not the other
# moves_string = ['e2e4', 'f7f5', 'e4e5', 'd7d5']

#7 about to do en passants
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5']

#8 en passant load, extra move(white did the en passant) 
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5', 'h5g6', 'h7h6', 'g6g7']

#9 en passant load, extra move(white did the en passant) 
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5', 'h5g6', 'h7h6']

#10 en passant load (white did the en passant)
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5', 'h5g6'] 

#11 pawns about to be promoted
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2']

#12 promoted pawns load 
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2', 'f7g8r', 'c2b1q']

#13 multiple pawns can be promoted to same square, or multiple pawns can be promoted to different squares
# moves_string = ['e2e4', 'd7d5', 'g2g4', 'b7b5', 'd2d3', 'c7c6', 'c1h6', 'g7h6', 'd1f3', 'd8a5', 'c2c3', 
#                 'a5b4', 'f3f6', 'e7f6', 'g4g5', 'b4b2', 'e4e5', 'b2d2', 'e1d2', 'b5b4', 'e5e6', 'd5d4', 'g5g6', 
#                 'c6c5', 'b1a3', 'c5c4', 'd3c4', 'b4b3', 'g6g7', 'd4d3', 'e6e7', 'b3b2', 'd2e3', 'd3d2', 'a1c1']

#14 pawn can't be promoted because it is pinned
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 
#                 'c2c3', 'b7b5', 'a2a3', 'b5b4', 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2']

#15 multiple pieces to same square
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5']

#16 two pinned knights
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1', 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e3c4']

#17 two knights can move two same square, but one is pinned
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1', 
#                 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                 'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7']

#18 two knights can move to same spot, but both are pinned from different directions
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1',
#                  'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                  'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7', 'd2d3', 'e7e6', 'h2h3', 'f8b4']

#19 two nights are both pinned from different directions, but can't move to the same spot like the scenario above
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 
#                 'e7e6', 'e2e1', 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                 'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7', 'd2d3', 'e7e6', 'h2h3', 'f8b4', 
#                 'h3h4', 'e6f6', 'e3g4', 'f6e7', 'g4e5', 'd7d6']

#20 illegal en passant (white king would be in check)
# moves_string = ['e2e4', 'c7c6', 'e1e2', 'b8a6', 'e2f3', 'a6b8', 'f3g4', 'b8a6', 'g4h5', 'd8a5', 'e4e5', 'd7d5']

#21 illegal en passant (black king would be in check)
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4', 'e5e4', 'f2f4']

#22 same scenario as above, but no pinned pawns
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4', 'a4a5', 'h2h4', 'e5e4', 'f2f4']

#23 loaded castling 
# moves_string = ['g1f3', 'g8f6', 'g2g4', 'g7g5', 'f1h3', 'f8h6', 'e1g1', 'e8g8']

#24 testing illegal castling scenarios. (black: kingside: can queenside: can't, white: kingside: can queenside: can)
# moves_string = ['g1f3', 'g8f6', 'g2g3', 'g7g6', 'f1h3', 'f8h6', 'c2c3', 'c7c6', 'd1b3', 'd8b6', 'd2d4', 'b8a6', 'c1f4', 'd7d5', 'b1a3', 'c8f5', 'b3d5']

#25 #about to be four move checkmate, black is about to loose
# moves_string = ['e2e3', 'b8a6', 'd1h5', 'g8h6', 'f1c4', 'h6g4',]

#26 #about to be four move checkmate, white is about to loose
# moves_string = ['g1h3', 'e7e6', 'b1a3', 'd8h4', 'a3b1', 'f8c5', 'h3g1']

#27 about to be a stalemate by repetition
# moves_string = ['g1f3', 'g8f6', 'f3g1', 'f6g8', 'g1f3', 'g8f6', 'f3g1']

#28 about to be a stalemate by repetition, with a bunch of moves inbetween (knight to c6)
# moves_string = ['g1f3', 'b8c6', 'g2g3', 'b7b6', 'f1h3', 'c8a6', 'b1c3', 'g8f6', 'f3g5', 'c6e5', 'g5f3', 'e5c6', 'f3g1', 'c6b8', 'c3b1', 'a6b7', 'b1c3', 'b7a6', 'g1f3']

#29 about to be stalemate, white king not in check but no white moves possible. (black pawn to e5 will cause this)
# moves_string = ['g1f3', 'e7e6', 'f3g1', 'd8h4', 'g1f3', 'h4h2', 'f3g1', 'h2h1', 'g1h3', 'h1h3', 'g2g4', 'h3g4', 'f2f4', 'g4f4', 'd2d4', 'f4d4', 'c2c4', 'd4c4', 
#                 'b2b4', 'c4b4', 'd1d2', 'b4b1', 'd2d1', 'b1c1', 'a2a3', 'c1a3', 'e1f2', 'a3a1', 'f2g3', 'a1d1', 'g3h4', 'd1e2', 'h4h3', 'e2f1', 
#                 'h3h4', 'g7g6', 'h4g5', 'f1f2', 'g5g4', 'd7d5', 'g4h3', 'f2g1', 'h3h4']

#30 about to be stalemate, black king not in check but no black moves possible. any move where the bishop on a7 is stil protected will be a stalemate. (queen to e5, king can take bishop. pawn to h3- stalemate.)
# moves_string =  ['e2e3', 'b8a6', 'd1g4', 'a6b8', 'g4g7', 'b8a6', 'g7h8', 'a6b8', 'h8h7', 'b8a6', 'h7g8', 
#                  'a6b8', 'g1f3', 'e7e6', 'f3g1', 'd8g5', 'g8g5', 'd7d5', 'g5d5', 'c7c5', 'd5c5', 'b7b6', 'c5b6', 
#                  'b8a6', 'b6a6', 'c8b7', 'a6b7', 'a7a6', 'b7a6', 'a8a7', 'a6a7', 'f7f5', 'a7c5', 'f8d6', 'c5d6', 
#                  'f5f4', 'd6f4', 'e6e5', 'f4e5', 'e8d8', 'f1b5', 'd8c8', 'e5d4', 'c8b8', 'b2b3', 'b8a8', 'c1a3', 
#                  'a8b8', 'a3c5', 'b8a8', 'b5a6', 'a8b8', 'c5a7', 'b8a8']

#31 multiple pawns can be promoted to same square, but one of them is pinned
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'c2c3', 'b7b5', 'a2a3', 'b5b4', 
#                 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2', 'h7h5', 'd1e1', 'h5h4', 'g2g4', 'h4g3', 
#                 'h2h4', 'g3f2', 'h1h2', 'g7g6', 'e1d1', 'g6g5', 'g1f3', 'g5g4', 'f3e1']

#32 multiple pawns can be promoted to same square, but both of them are pinned
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'c2c3', 'b7b5', 'a2a3', 
#                 'b5b4', 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2', 'h7h5', 'd1e1', 'h5h4', 'g2g4', 'h4g3', 
#                 'h2h4', 'g3f2', 'h1h2', 'g7g6', 'e1d1', 'g6g5', 'g1f3', 'g5g4', 'f3e1', 'd7d6', 'c3c4', 
#                 'd6e5', 'c4c5', 'e5d4', 'b2b3', 'd4d5', 'c1b2', 'd5e4', 'b2e5', 'e4d5', 'h2h3', 'd5e4', 
#                 'e5h2', 'e4d4', 'h2g1']

#33 about to be a draw by 50 moves (50 moves each side since the last time a pawn was moved or a piece was captured)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'd1e2', 'd5d4', 'e2e3', 'd4e4', 'b1c3', 'e4d4', 'e3f3', 'd4e4', 'f1e2', 'e4e3', 
#                 'f3e4', 'e3f4', 'e4f5', 'f4g5', 'f5g4', 'g5h4', 'g4a4', 'b8c6', 'a4g4', 'h4g5', 'g4h5', 'g5a5', 'h5h3', 'a5b4', 
#                 'h3g4', 'c6e5', 'g1f3', 'b4e4', 'f3g5', 'e5f3', 'e1f1', 'f3d4', 'g4f4', 'e4f5', 'f4e3', 'f5h3', 'e3e5', 'h3f5', 
#                 'e5c5', 'f5d5', 'c5c4', 'd5c5', 'c4b4', 'c5c4', 'b4b3', 'c4b4', 'b3a4', 'd4b5', 'a4b3', 'b4e4', 'b3d5', 'e4d4', 
#                 'd5e5', 'd4e4', 'c3d5', 'e4d4', 'g5f3', 'g8f6', 'd5c3', 'b5d6', 'c3e4', 'f6d5', 'f3g5', 'd6b5', 'e5f5', 'd5c3', 
#                 'f5g4', 'd4e5', 'g4f3', 'e5f5', 'f3d3', 'f5f3', 'd3d5', 'f3f5', 'd5e5', 'f5e6', 'e5f5', 'e6e5', 'f5f6', 'c3d5', 
#                 'g5f3', 'b5c3', 'f6f5', 'e5d4', 'f5e5', 'd4c5', 'e5d4', 'c5d6', 'd4e5', 'd6c5', 'e5h5', 'c3b5', 'h5g4', 'c5a3', 
#                 'g4g5', 'b5c3', 'g5e5', 'c3b5', 'e5d6']

#34 about to be draw by insufficient material (king vs king)
# moves_string = ['e2e4', 'd7d5', 'd1h5', 'd8d6', 'h5d5', 'd6e5', 'd5f7', 'e8d8', 'f7g8', 'e5b2', 'g8h8', 'b2a1', 'h8h7', 'a1a2', 'h7g7', 
#                 'a2b1', 'g7f8', 'd8d7', 'f8c8', 'd7c6', 'c8b8', 'b1c1', 'e1e2', 'c1c2', 'b8a8', 'c2d2', 'e2f3', 'd2f2', 'f3g4', 'f2g1', 
#                 'a8a7', 'g1g2', 'g4f5', 'g2h1', 'a7b7', 'c6c5', 'b7c7', 'c5d4', 'c7e7', 'h1h2', 'e7h4', 'h2f4', 'f5f4', 'd4c5', 'f4f3', 
#                 'c5d6', 'f3g2', 'd6e5', 'h4f4', 'e5d4', 'f4h6', 'd4e4', 'f1d3', 'e4d3', 'h6e3']

#35 about to be draw by insufficient material (black king vs white bishop and white king)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'c2c4', 'd5c4', 'd2d3', 'c4c3', 'e1e2', 'c3b2', 'e2e1', 'b2a2', 'd1a4', 'c7c6', 'a4a7', 'a2a1', 
#                 'a7a8', 'a1b1', 'a8b8', 'b1d3', 'b8b7', 'd3f1', 'e1d2', 'f1g1', 'b7c6', 'e8d8', 'c6h6', 'g1h1', 'h6h7', 'h1h2', 'h7h8', 'h2g2', 
#                 'h8g8', 'g2f2', 'd2d1', 'f2g3', 'g8g7', 'g3g2', 'g7f7', 'g2g3', 'f7e7', 'f8e7', 'd1e2', 'g3e3', 'e2e3', 'e7g5', 'e3f3', 'g5f4', 'f3f4', 'c8g4']

#36 about to be draw by insufficient material (white king vs black bishop and black king)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'c2c4', 'd5c4', 'd2d3', 'c4c3', 'e1e2', 'c3b2', 'e2e1', 'b2a2', 'd1a4', 'c7c6', 'a4a7', 'a2a1', 
#                 'a7a8', 'a1b1', 'a8b8', 'b1d3', 'b8b7', 'd3f1', 'e1d2', 'f1g1', 'b7c6', 'e8d8', 'c6h6', 'g1h1', 'h6h7', 'h1h2', 'h7h8', 'h2g2', 
#                 'h8g8', 'g2f2', 'd2d1', 'f2g3', 'g8g7', 'g3g2', 'g7f7', 'g2g3', 'f7e7', 'f8e7', 'd1e2', 'g3e3', 'e2e3', 'e7g5', 'e3f3', 'g5f4', 
#                 'f3f4', 'c8g4', 'f4g3', 'g4f3', 'c1a3', 'd8d7', 'a3e7']

#37 about to be draw by insufficient material (white king and white bishop vs black bishop and black king, bishops are of the same color - dark squares)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'c2c4', 'd5c4', 'd2d3', 'c4c3', 'e1e2', 'c3b2', 'e2e1', 'b2a2', 'd1a4', 'c7c6', 'a4a7', 'a2a1', 
#                 'a7a8', 'a1b1', 'a8b8', 'b1d3', 'b8b7', 'd3f1', 'e1d2', 'f1g1', 'b7c6', 'e8d8', 'c6h6', 'g1h1', 'h6h7', 'h1h2', 'h7h8', 'h2g2', 
#                 'h8g8', 'g2f2', 'd2d1', 'f2g3', 'g8g7', 'g3g2', 'g7f7', 'g2g3', 'f7e7', 'f8e7', 'd1e2', 'g3e3', 'e2e3', 'e7g5', 'e3f3']

#38 about to be draw by insufficient material (white king and white bishop vs black bishop and black king, bishops are of the same color - light squares)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'd1h5', 'd5g2', 'h5h7', 'g2h1', 'h7h8', 'h1h2', 'h8g7', 'h2f2', 'e1d1', 'e8d8', 'b1c3', 'b8c6', 
#                 'c3e4', 'c6e5', 'g1f3', 'g8f6', 'f3d4', 'f6d5', 'd2d3', 'e7e6', 'c1f4', 'f8c5', 'g7f7', 'f2c2', 'd1e1', 'c2b2', 'f7c7', 'd8e8', 
#                 'c7b7', 'b2a2', 'b7a8', 'a2a1', 'e1f2', 'a1d1', 'a8a7', 'd1d3', 'a7a6', 'c8b7', 'a6e6', 'e8f8', 'e6e5', 'd3d4', 'f2e1', 'd4e4', 
#                 'e1d1', 'e4f4', 'e5d5', 'b7a6', 'd5c5', 'f8f7', 'c5f8', 'f7f8', 'd1e1', 'f4d2']

#39 about to be draw by insufficient material (king vs knight and king, black or white)
# moves_string = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'd1h5', 'd5g2', 'h5h7', 'g2h1', 'h7h8', 'h1h2', 'h8g7', 'h2f2', 'e1d1', 'e8d8', 'b1c3', 'b8c6', 
#                 'c3e4', 'c6e5', 'g1f3', 'g8f6', 'f3d4', 'f6d5', 'd2d3', 'e7e6', 'c1f4', 'f8c5', 'g7f7', 'f2c2', 'd1e1', 'c2b2', 'f7c7', 'd8e8', 
#                 'c7b7', 'b2a2', 'b7a8', 'a2a1', 'e1f2', 'a1d1', 'a8a7', 'd1d3', 'a7a6', 'c8b7', 'a6e6', 'e8f8', 'e6d6', 'f8f7', 'd6c5', 'b7c6', 
#                 'c5c6', 'd3f3', 'f2g1', 'f3f4', 'g1g2', 'f4f1', 'g2f1', 'f7e7', 'c6e6', 'e7d8', 'e6e8', 'd8e8', 'e4f6', 'e8f7', 'f1e2', 'f7f6', 
#                 'e2d2', 'e5d3', 'd2d3']

#40 two promoted rooks can move to the same spot. g7 works, f8 doesn't.
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 
#                 'd3c2', 'f7g8r', 'c2b1q', 'h3h4', 'g7g5', 'h4g5', 'h7h5', 'g5g6', 'h8h6', 'g6g7', 'h6a6', 'g7f8r', 'a6b6', 'f8f7', 'b6c6']

#41 two promoted knights can move to the same spot, this one works
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2', 'f7g8n', 'd8e8', 'f2f4', 'b8c6', 'f4f5', 'c6d4', 'f5f6', 'e7e5', 'f6f7', 'e5e4', 'f7e8n', 'e4e3']
#moves_string = [] #empty new game

#42 two promoted knights can move to g8
moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2', 'f7g8n', 'd8e8', 'f2f4', 'b8c6', 
                'f4f5', 'c6d4', 'f5f6', 'e7e5', 'f6f7', 'e5e4', 'f7e8n', 'e4e3', 'e8f6', 'd7d8', 'g8h6', 'a7a6']

#43 two normal knights can move b8, doesn't work
# moves_string = ['g1f3', 'h7h6', 'f3d4', 'h6h5', 'd2d3', 'h5h4', 'b1d2', 'h4h3', 'd2b3', 'g7g6', 'b3c5', 'g6g5', 'c5a6', 'g5g4', 'd4c6', 'g4g3']

#44 two normal knights can move d1, doesn't work (black)
# moves_string = ['g1f3', 'g8f6', 'b1c3', 'b8c6', 'f3e5', 'f6g4', 'c3d5', 'c6a5', 'h2h4', 'g4e3', 'h4h5', 'a5c4', 'h5h6', 'c4a3', 'h6g7', 'a3b5', 'g7h8q', 'b5c3', 'g2g3']

#45 two normal knights can move d1, doesn't work (black)
# moves_string = ['g1f3', 'g8f6', 'b1c3', 'b8c6', 'f3e5', 'f6g4', 'c3d5', 'c6a5', 'h2h4', 'g4e3', 'h4h5', 'a5c4', 'h5h6', 'c4a3', 'h6g7', 'a3b5', 'g7h8q', 'b5c3', 'g2g3']

#46 two normal knights can move d1, loading it works
# moves_string = ['g1f3', 'g8f6', 'b1c3', 'b8c6', 'f3e5', 'f6g4', 'c3d5', 'c6a5', 'h2h4', 'g4e3', 'h4h5', 'a5c4', 'h5h6', 'c4a3', 'h6g7', 'a3b5', 'g7h8q', 'b5c3', 'g2g3', 'e3d1']

#47 about to be a stalemate by repetition, (knight to g8)
# moves_string = ['g1f3', 'g8f6', 'f3g1', 'f6g8', 'g1f3', 'g8f6', 'f3g1']

#48 pawn promotion to corners ###error promoting rook and queen
# moves_string = ['e2e4', 'f7f5', 'd2d3', 'f5e4', 'd1e2', 'e4d3', 'c2d3', 'e7e5', 'd3d4', 'd8e7', 'e2e5', 'e7e5', 'd4e5', 'g8f6', 'e5f6', 'h7h6', 'f6g7', 'c7c5', 'b2b4', 'c5b4', 'f2f3', 'b4b3', 'f3f4', 'b3b2']

# moves_string = []

#used to update the current list of moves made, and transitively the current position. Can be used in tandem with above set position to set a position before playing 
all_moves = moves_string
board_positions_list = []

#dictionary used to track all the piece positions. Keeps track of specific pieces of same type
position_dict = {
    'Piece.white_KING': "",
    'Piece.white_QUEEN': "",
    'Piece.white_BISHOP1': "",
    'Piece.white_BISHOP2': "",
    'Piece.white_KNIGHT1': "",
    'Piece.white_KNIGHT2': "",
    'Piece.white_ROOK1': "",
    'Piece.white_ROOK2': "",
    'Piece.white_PAWN1': "",
    'Piece.white_PAWN2': "",
    'Piece.white_PAWN3': "",
    'Piece.white_PAWN4': "",
    'Piece.white_PAWN5': "",
    'Piece.white_PAWN6': "",
    'Piece.white_PAWN7': "",
    'Piece.white_PAWN8': "",
    
    # 'Piece.PROMOTED_white_PAWN1': "",
    # 'Piece.PROMOTED_white_PAWN2': "",
    # 'Piece.PROMOTED_white_PAWN3': "",
    # 'Piece.PROMOTED_white_PAWN4': "",
    # 'Piece.PROMOTED_white_PAWN5': "",
    # 'Piece.PROMOTED_white_PAWN6': "",
    # 'Piece.PROMOTED_white_PAWN7': "",
    # 'Piece.PROMOTED_white_PAWN8': "",


    'Piece.black_KING': "",
    'Piece.black_QUEEN': "",
    'Piece.black_BISHOP1': "",
    'Piece.black_BISHOP2': "",
    'Piece.black_KNIGHT1': "",
    'Piece.black_KNIGHT2': "",
    'Piece.black_ROOK1': "",
    'Piece.black_ROOK2': "",
    'Piece.black_PAWN1': "",
    'Piece.black_PAWN2': "",
    'Piece.black_PAWN3': "",
    'Piece.black_PAWN4': "",
    'Piece.black_PAWN5': "",
    'Piece.black_PAWN6': "",
    'Piece.black_PAWN7': "",
    'Piece.black_PAWN8': "",
    
    # 'Piece.PROMOTED_black_PAWN1': "",
    # 'Piece.PROMOTED_black_PAWN2': "",
    # 'Piece.PROMOTED_black_PAWN3': "",
    # 'Piece.PROMOTED_black_PAWN4': "",
    # 'Piece.PROMOTED_black_PAWN5': "",
    # 'Piece.PROMOTED_black_PAWN6': "",
    # 'Piece.PROMOTED_black_PAWN7': "",
    # 'Piece.PROMOTED_black_PAWN8': "",
}

captured_pieces_list = []

#helper dictionary to print the board
symbols_dict = {
    'king': "k",
    'queen': "q",
    'bishop': "b",
    'knight': "n",
    'rook': "r",
    'pawn': "p",
}

#dictionary used print the board to the screen.
board_dict = {
    'A1': "",
    'A2': "",
    'A3': "",
    'A4': "",
    'A5': "",
    'A6': "",
    'A7': "",
    'A8': "",

    'B1': "",
    'B2': "",
    'B3': "",
    'B4': "",
    'B5': "",
    'B6': "",
    'B7': "",
    'B8': "",

    'C1': "",
    'C2': "",
    'C3': "",
    'C4': "",
    'C5': "",
    'C6': "",
    'C7': "",
    'C8': "",

    'D1': "",
    'D2': "",
    'D3': "",
    'D4': "",
    'D5': "",
    'D6': "",
    'D7': "",
    'D8': "",

    'E1': "",
    'E2': "",
    'E3': "",
    'E4': "",
    'E5': "",
    'E6': "",
    'E7': "",
    'E8': "",

    'F1': "",
    'F2': "",
    'F3': "",
    'F4': "",
    'F5': "",
    'F6': "",
    'F7': "",
    'F8': "",

    'G1': "",
    'G2': "",
    'G3': "",
    'G4': "",
    'G5': "",
    'G6': "",
    'G7': "",
    'G8': "",

    'H1': "",
    'H2': "",
    'H3': "",
    'H4': "",
    'H5': "",
    'H6': "",
    'H7': "",
    'H8': "",
}

#all of the chess pieces, and what they could be mistaken for
pieces = {
    "king": ["king"],
    "queen": ["queen", "lady"],
    "rook": ["rook", "castle"],
    "bishop": ["bishop", "clergy"],
    "knight": ["knight", "night", "horse", "nigh", "nite"],
    "pawn": ["pawn", "pond", "upon", "ponder", "panda", "power", "pontiff", "pine"]
}

##I'm having trouble deciphering one intent from another, because of how they use a lot of the same words
#intents that are not a specific move, rather a command to change the game type or status
intents = {
    "restart": ["restart", "reset the game", "reset the board", "start over", "play again", "retry", "begin again", "reset"],
    "start": ["start", "new game", "set the board", "set the bored"],
    "undo": ["undo", "redo", "go back", "reverse", "take back move", "previous move", 
        "step back", "revert", "undo last action", "back"],
    "end": ["end", "end game", "quit", "stop playing", "exit", "close game", 
        "game over", "finish game", "shut down", "resign"],
    "takeover": ["take over", "takeover", "replace"],
    "list": ["list", "list commands", "options"]
}

confirmation_responses = {
    "affirmative": [
        "yes", "yeah", "yep", "yup", "sure", "of course", "definitely", "absolutely", 
        "certainly", "indeed", "affirmative", "roger", "aye", "ok", "okay", "fine", 
        "you bet", "totally", "uh-huh", "alright", "sure thing", "for sure", "why not"
    ],
    "negative": [
        "no", "nope", "nah", "not at all", "never", "absolutely not", "no way", 
        "negative", "nay", "uh-uh", "not really", "i don't think so", "by no means", 
        "no thanks", "no thank you", "not happening", "out of the question", "forget it", "cancel"
    ]
}

#different ways to say castle
castles = {
    "Kingside": ["castle king side", "castle kingside", "castle kings i'd", "castle kings hide", "castle king's side", "castle kings side",
    "castle on king side", "castle on kingside", "castle on kings i'd", "castle on kings hide", "castle on king's side", "castle on kings side",
    "castle on the king side", "castle on the kingside", "castle on the kings i'd", "castle on the kings hide", "castle on the king's side", "castle on the kings side",
    "king side castle", "kingside castle", "kings i'd castle", "kings hide castle", "king's side castle", "kings side castle"],

    "Queenside": ["castle queen side", "castle queenside", "castle queens i'd", "castle queens hide", "castle queen's side", "castle queens side",
    "castle on queen side", "castle on queenside", "castle on queens i'd", "castle on queens hide", "castle on queen's side", "castle on queens side",
    "castle on the queen side", "castle on the queenside", "castle on the queens i'd", "castle on the queens hide", "castle on the queen's side", "castle on the queens side",
    "queen side castle", "queenside castle", "queens i'd castle", "queens hide castle", "queen's side castle", "queens side castle"],
}

#all of the letters of squares, and what they could be mistaken for
letter_squares_separate = {
    "A": ["a", "eh", "day", "pay"],
    "B": ["b", "bee", "be"],
    "C": ["c", "see", "sea"],
    "D": ["d", "dee"],
    "E": ["e", "he", "eat ", "ie"],
    #All the f's are giving me a real headache. Vosk really doesn't recognize it. 
    "F": ["f", "have", "def", "after", "ask"],
    "G": ["g", "gee", "geez"],
    "H": ["h"]
}

#all of the numbers of squares, and what they could be mistaken for
number_squares_separate = {
    "1": ["one", "1", "juan", "yawn", "won"],
    "2": ["two", "2", "too", "to"],
    "3": ["three", "3", "tree", "free"],
    "4": ["four", "4", "for", "floor"],
    "5": ["five", "5", "fight", "hive"],
    "6": ["six", "6", "sex", "sick", "sicks"],
    "7": ["seven", "7"],
    "8": ["eight", "8", "ate", "hate", "paid"]
}

#all of the squares with the letters and numbers together, and what they could be mistaken for
squares_together = {
    "A1": ["a1"],
    "A2": ["a2"],
    "A3": ["a3"],
    "A4": ["a4"],
    "A5": ["a5"],
    "A6": ["a6"],
    "A7": ["a7"],
    "A8": ["a8"], 

    "B1": ["b1"],
    "B2": ["b2"],
    "B3": ["b3"],
    "B4": ["b4", "before"],
    "B5": ["b5"],
    "B6": ["b6"],
    "B7": ["b7"],
    "B8": ["b8"],

    "C1": ["c1"],
    "C2": ["c2"],
    "C3": ["c3"],
    "C4": ["c4", "seafloor"],
    "C5": ["c5"],
    "C6": ["c6"],
    "C7": ["c7"],
    "C8": ["c8"],

    "D1": ["d1"],
    "D2": ["d2", "detour"],
    "D3": ["d3"],
    "D4": ["d4", "defer"],
    "D5": ["d5"],
    "D6": ["d6"],
    "D7": ["d7"],
    "D8": ["d8"],

    "E1": ["e1"],
    "E2": ["e2"],
    "E3": ["e3"],
    "E4": ["e4"],
    "E5": ["e5"],
    "E6": ["e6"],
    "E7": ["e7"],
    "E8": ["e8"],

    #All the f's are giving me a real headache. Vosk really doesn't recognize it. 
    "F1": ["f1"],
    "F2": ["f2"],
    "F3": ["f3"],
    "F4": ["f4"],
    "F5": ["f5"],
    "F6": ["f6"],
    "F7": ["f7"],
    "F8": ["f8", "fate"],

    "G1": ["g1"],
    "G2": ["g2"],
    "G3": ["g3"],
    "G4": ["g4"],
    "G5": ["g5"],
    "G6": ["g6"],
    "G7": ["g7"],
    "G8": ["g8", "gate"],

    "H1": ["h1"],
    "H2": ["h2"],
    "H3": ["h3"],
    "H4": ["h4"],
    "H5": ["h5"],
    "H6": ["h6"],
    "H7": ["h7"],
    "H8": ["h8"],
}

#testing a global turn
global_turn = "white"

first_time = True

fifty_move_rule_count = 0
fifty_move_rule_bool = False

#load in data from another game
def set_position(moves_string_list):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time, board_positions_list
    moves = moves_string_list.copy()  #shallow copy of the list
    castle_moves_list = ["e1g1", "e1c1", "e8g8", "e8c8"]
    castle_data = {
        "e1g1": "Castle Kingside",
        "e8g8": "Castle Kingside",
        "e1c1": "Castle Queenside",
        "e8c8": "Castle Queenside"
    }
    
    loaded_last_move = ""
    # print(moves)
    temp_all_moves = []
    for move in moves:
        # print_board_visiual()
        # input()

        #remember loading pawn promotions
        if len(move) == 5:
            piece = phoenix.abbreviation_dict[move[-1].lower()]
            position_dict, all_moves, global_turn, board_positions_list = phoenix.implement_command(move, piece, update=False, loaded_last_move=loaded_last_move, position_dict=position_dict, all_moves=temp_all_moves, board_positions_list=board_positions_list)
        
        #remember loading castling
        elif move in castle_moves_list: 
            position_dict, all_moves, global_turn, board_positions_list = phoenix.implement_command(move, castle_data[move], update=False, loaded_last_move=loaded_last_move, position_dict=position_dict, all_moves=temp_all_moves, board_positions_list=board_positions_list)

        #everthing else
        else: 
            position_dict, all_moves, global_turn, board_positions_list = phoenix.implement_command(move, "fluff", update=False, loaded_last_move=loaded_last_move, position_dict=position_dict, all_moves=temp_all_moves, board_positions_list=board_positions_list) #implement command ("fluff") doesn't actually use this unless it is for castling. need to fix that.
            clear_screen()
        loaded_last_move = move
        check_for_50_move_draw(move) 
        temp_all_moves.append(move)

#print all the moves that have occurred so far
def print_all_moves():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    print(f"all_moves: {all_moves}")

#main
def main():
    set_initials()
    play_game_loop()

#the game loop
def play_game_loop():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time, board_positions_list
    if first_time:
        words = input(f"Hello and welcome to the world of magic chess! My name is Phoenix. You can resume a recent game or start a new game. {get_turn_color().capitalize()} to move, please state a command: ")
        first_time = False
    else: words = input(f"{get_turn_color().capitalize()} to move. Please state a command: ")
    
    if words == "all moves":
        print_all_moves()
        play_game_loop()
    elif words.lower() == "position dict":
        print(position_dict)
        play_game_loop()
    elif words.lower() == "possible moves":
        print(phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves))
        play_game_loop()
    elif words.lower() == "board positions list":
        print_board_positions()
        play_game_loop()
    elif words.lower() == "50 move logic":
        print(f"fifty_move_rule_count: {fifty_move_rule_count}\nfifty_move_rule_bool: {fifty_move_rule_bool}\ncaptured_pieces_list: {captured_pieces_list}")
        play_game_loop()
        
    intention_check = check_intentions(words) 
    #if there is an intention instead of a move   
    if intention_check: process_intention(intention_check)

    #decipher the command out of the words
    #if the move isn't possible, then the command is the error message
    (command, possible), piece = decipher_command(words)

    if possible: 
        position_dict, all_moves, global_turn, board_positions_list = phoenix.implement_command(command, piece, position_dict=position_dict, all_moves=all_moves, board_positions_list=board_positions_list)
        check_for_50_move_draw(command) 

    clear_screen()
    print_board_visiual()

    #if there are no available moves for the person that did not just make a move in this function (aka whose turn it is), then it is either a checkmate or a stalemate
    if len(phoenix.get_possible_moves(turn = get_turn_color(), position_dict=position_dict, all_moves=all_moves)) == 0:
        if phoenix.is_king_in_check(get_turn_color(), position_dict=position_dict, all_moves=all_moves): print(f"Game over, {'black' if get_turn_color().lower() == 'white' else 'white'} wins by checkmate")
        else: print(f"Game over by stalemate. {get_turn_color().lower()} doesn't have any legal moves.")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()

    # print(f"check_for_repetition_draw(): {check_for_repetition_draw()}")
    if check_for_repetition_draw():
        print(f"Game over - stalemate by repetition")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()

    if fifty_move_rule_bool:
        print(f"Game over - draw by 50 move rule")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()

    if check_for_insufficient_material_draw():
        print(f"Game over - draw by insufficient material")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()

    #print (or say) the command
    print(command)
    if phoenix.is_king_in_check(get_turn_color(), position_dict=position_dict, all_moves=all_moves): print(f"{get_turn_color()} king is in check")
    # print(f"current position status: {phoenix.evaluate_postion(position_dict)}")
    
    print(phoenix.get_legal_pawn_normal_moves(phoenix.phoenix_get_turn_from_moves(all_moves), position_dict, all_moves))
    print_phoenix_best_move()

    if words != "quit":
        play_game_loop()
    else:
        print("Thanks for playing, play again soon! \n-Pheonix")

#can also be used to test things before the game starts
def set_initials():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time, fifty_move_rule_bool, fifty_move_rule_count
    reset_50_move_logic()
    locate_pieces_initial()
    board_positions_list.append(get_initial_board_position())
    set_position(all_moves)
    get_turn_from_moves(all_moves)
    clear_screen()
    print_board_visiual()

def print_phoenix_best_move():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time, fifty_move_rule_bool, fifty_move_rule_count

    position_dict_copy = position_dict.copy()
    board_positions_list_copy = board_positions_list.copy()

    move, evaluation = get_best_move(
    2,
    phoenix.phoenix_get_turn_from_moves(all_moves),
    position_dict_copy,
    all_moves,
    board_positions_list_copy,
    alpha=float('-inf'),
    beta=float('inf'),
    maximizing_player=True  # or False, depending if it's white's turn or black's
    )

    print(f"Phoenix recommends move {move}")

def reset_global_turn():
    global global_turn
    global_turn = "white"

def reset_50_move_logic():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time, fifty_move_rule_bool, fifty_move_rule_count
    fifty_move_rule_count = 0
    fifty_move_rule_bool = False
    captured_pieces_list.clear()

#it is white if there have been no moves, otherwise count the moves_string
def get_turn_from_moves(moves):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if len(moves) > 0: global_turn = "black" if len(moves) % 2 == 1 else "white"
    else: global_turn = "white"

#change the turn color from white to black, and from black to white
def toggle_turn_color():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    global_turn = "black" if global_turn == "white" else "white"

def get_pieces_initial():
    return {
        'Piece.white_KING': 'e1', 
        'Piece.white_QUEEN': 'd1', 
        'Piece.white_BISHOP1': 'c1', 
        'Piece.white_BISHOP2': 'f1', 
        'Piece.white_KNIGHT1': 'b1', 
        'Piece.white_KNIGHT2': 'g1', 
        'Piece.white_ROOK1': 'a1', 
        'Piece.white_ROOK2': 'h1', 
        'Piece.white_PAWN1': 'a2', 
        'Piece.white_PAWN2': 'b2', 
        'Piece.white_PAWN3': 'c2', 
        'Piece.white_PAWN4': 'd2', 
        'Piece.white_PAWN5': 'e2', 
        'Piece.white_PAWN6': 'f2', 
        'Piece.white_PAWN7': 'g2', 
        'Piece.white_PAWN8': 'h2', 
        'Piece.black_KING': 'e8', 
        'Piece.black_QUEEN': 'd8', 
        'Piece.black_BISHOP1': 'c8', 
        'Piece.black_BISHOP2': 'f8', 
        'Piece.black_KNIGHT1': 'b8', 
        'Piece.black_KNIGHT2': 'g8', 
        'Piece.black_ROOK1': 'a8', 
        'Piece.black_ROOK2': 'h8', 
        'Piece.black_PAWN1': 'a7', 
        'Piece.black_PAWN2': 'b7', 
        'Piece.black_PAWN3': 'c7', 
        'Piece.black_PAWN4': 'd7', 
        'Piece.black_PAWN5': 'e7', 
        'Piece.black_PAWN6': 'f7', 
        'Piece.black_PAWN7': 'g7', 
        'Piece.black_PAWN8': 'h7'
        }

#Locates all of the initial pieces' positions, and puts them in the positions dictionary
def locate_pieces_initial():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    position_dict_temp = get_pieces_initial()
    for temp, position in position_dict_temp.items():
        position_dict[temp] = position

#pring position dict for debugging
def print_position_dict_debugging():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    temp_location_list = []
    for number in ["8", "7", "6", "5", "4", "3", "2", "1"]:
        for letter in ["a", "b", "c", "d", "e", "f", "g", "h"]:
            for piece, position in position_dict.items():
                square = f"{letter}{number}"
                if position == square: temp_location_list.append(f"{position}: {piece}")
    
    # print(temp_location_list)
    print("\n".join(" ".join(temp_location_list[i:i+8]) for i in range(0, len(temp_location_list), 8)))

#prints the board
def print_board_visiual():
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    #clear the board dict
    for square, piece in board_dict.items():
        board_dict[square] = ""
    
    #assign the board dict according to the position dict
    for piece, square in position_dict.items():
        if square and (square != "xx"): 
            board_dict[square.upper()] = piece

    # Go from 8 to 1, and print each line and lane (lane contains characters)
    for i in range(8, 0, -1):
        print_line()
        print_lane(*[get_symbol(letter, i) for letter in "ABCDEFGH"], i)
    
    #print the last line and the column letters
    print_line()
    print_end_line()

#helper function for print board visual
def get_symbol(letter, number): 
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    key = f"{letter}{number}"
    piece = check_for_pieces(board_dict[key])
    if piece: return str(symbols_dict[piece]).upper() if "white" in board_dict[key].lower() else str(symbols_dict[piece])
    else: return " "

#print line on the chess board
def print_line():
    print("+---+---+---+---+---+---+---+---+")
    
#print line on the end of the chess board
def print_end_line():
    print(f"  a   b   c   d   e   f   g   h\n")

#print line on the chess board
def print_lane(a, b, c, d, e, f, g, h, number):
    print(f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} | {h} | {number}")

#uses the board_position_list to compare all of the board's past positions, and see if there are 3 repetitions of them
def check_for_repetition_draw():
    global board_positions_list
    # Convert each inner list to a tuple so it can be counted
    hashable_positions = [tuple(position) for position in board_positions_list]
    counts = Counter(hashable_positions)
    return any(count >= 3 for count in counts.values())

def check_for_50_move_draw(move):
    global fifty_move_rule_count, position_dict, captured_pieces_list, fifty_move_rule_bool
    pawn_moved, piece_taken = False, False

    for piece, position in position_dict.items():
        #check if the last two in move are a pawn, means a pawn was moved
        if (move[-2:] == position) and ("pawn" in piece.lower()) and ("promoted" not in piece.lower()): 
            pawn_moved = True
        
        #check if a piece was taken this move
        if position == "xx":
            if piece.lower() not in captured_pieces_list:
                captured_pieces_list.append(piece.lower())
                piece_taken = True

    if pawn_moved or piece_taken:
        fifty_move_rule_count = 0
        return False
    else:
        fifty_move_rule_count += 1
        if fifty_move_rule_count >= 100: fifty_move_rule_bool = True
        return True

def check_for_insufficient_material_draw():
    black_bishop_count_total = 0
    black_dark_bishop_count = 0
    black_light_bishop_count = 0

    white_bishop_count_total = 0
    white_dark_bishop_count = 0
    white_light_bishop_count = 0

    black_knight_count = 0
    white_knight_count = 0

    for piece, position in position_dict.items():
        #any position that has a queen is not insufficient material
        if "queen" in piece.lower() and position and position != "xx": return False
        #same with rook
        if "rook" in piece.lower() and position and position != "xx": return False
        #same with pawn (can be promoted)
        if "pawn" in piece.lower() and position and position != "xx": return False
        #black bishop count
        if "bishop" in piece.lower() and "black" in piece.lower() and position and position != "xx": 
            black_bishop_count_total += 1
            if is_dark_square(position): black_dark_bishop_count += 1
            else: black_light_bishop_count += 1
        #white bishop count
        if "bishop" in piece.lower() and "white" in piece.lower() and position and position != "xx": 
            white_bishop_count_total += 1
            if is_dark_square(position): white_dark_bishop_count += 1
            else: white_light_bishop_count += 1
        #black bishop count
        if "knight" in piece.lower() and "black" in piece.lower() and position and position != "xx": black_knight_count += 1
        #white bishop count
        if "knight" in piece.lower() and "white" in piece.lower() and position and position != "xx": white_knight_count += 1

    # king vs king

    if all(x == 0 for x in [black_bishop_count_total, white_bishop_count_total, black_knight_count, white_knight_count]): return True

    # king and bishop vs king
    elif black_bishop_count_total + white_bishop_count_total == 1: return True
    
    # king and knight vs king
    elif black_knight_count + white_knight_count == 1: return True
    
    # king and bishop vs king and bishop (same-colored bishops)
    #One black dark bishop and one white dark bishop, and no light bishops
    elif ((black_dark_bishop_count == 1 and white_dark_bishop_count == 1 and black_light_bishop_count == 0 and white_light_bishop_count == 0) or 
    # or One black light bishop and one white light bishop, and no dark bishops
    (black_light_bishop_count == 1 and white_light_bishop_count == 1 and black_dark_bishop_count == 0 and white_dark_bishop_count == 0)) and \
    (black_bishop_count_total + white_bishop_count_total == 2): return True #And no other bishops
    else: return False #example: two black bishops and one white bishops left

#used by check for insufficient material to see if a bishop is on a dark or light
def is_dark_square(square):
    file = square[0].lower()  # e.g., 'e'
    rank = int(square[1])     # e.g., 4

    # Convert file letter to a number (a=1, b=2, ..., h=8)
    file_index = ord(file) - ord('a') + 1

    # Dark if sum is even, light if odd
    return (file_index + rank) % 2 == 0

#used for debugging the board positions list
def print_board_positions():
    global board_positions_list
    # Convert each inner list to a tuple so it can be counted
    hashable_positions = [tuple(position) for position in board_positions_list]
    counts = Counter(hashable_positions)
    for list, count in counts.items():
        print(f"{list}: {count}\n")

#prints possibles moves, not currently used
def print_possible_moves():
    global all_moves, position_dict
    print(f"Possible moves: {phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves)}")

#process words and parse word command
def decipher_command(words): 
    command, piece, square = process_words(words)
    return parse_word_command(piece, square, command), piece

#decipher the command out of the given words
#command (e2e4), piece (pawn), square (e4) = process_words(words)
def process_words(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time

    #remove everything before phoenix
    words = remove_before_word(words, "phoenix")

    #check if the words have phrases for a castle. If not, it is ignored and continues on.
    castling = check_for_castles(words)
    if castling:
        #if there is a castle, return it. Done with process_words
        return "castle", castling, None

    #check if the phrases contains chess pieces
    #if there is more than one piece, or no pieces, found_piece is false. Done with process_words
    #else, continue on
    found_piece = check_for_pieces(words)
    # print(f"found_piece: {found_piece}")
    if not found_piece:
        # print("no found piece")
        return False, None, None

    #Check if there is a valid square.
    #parse the resulting command out of the found_piece and square. Done with process_words
    #else, no valid command. Done with process_words
    square = check_square(words)
    if square:
        # result = f"Moving {found_piece} to {square}..."
        result = f"{found_piece} to {square}"
        return result, found_piece, square
    else:
        # print("no square")
        return False, None, None

#takes the command (pawn to E4) and turns it into -> e2e4
#does this by looking at each pawns initial position, splicing it with the wanted position, and then seeing if any of those are legal
#first it splices all the squares from piece type spaces with the wanted_position, and filters out the ones that aren't legal
#The it counts how many there are, and checks how many of them are legal if king is in not in check after.
#It then continues with the command, clarifies which piece to move, or displays the appropriate error message.
def parse_word_command(piece, wanted_position, command):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if piece is not None:
        possible_piece_moves = []
        found_piece = ""

        if command == "castle":
            return parse_castle_command(piece)

        piece_positions = phoenix.piece_type_spaces(piece, get_turn_color(), position_dict=position_dict, all_moves=all_moves)
        for position in piece_positions:
            possible_piece_moves.append(f"{position}{wanted_position.lower()}")
            if position and piece == "pawn" and ((wanted_position[-1] == "8" and position[1] == "7") or (wanted_position[-1] == "1" and position[1] == "2")):
                    for abbreviation, abbreviation_piece in phoenix.abbreviation_dict.items():
                        if abbreviation not in ["k", "p"]:
                            possible_piece_moves.append(f"{position}{wanted_position.lower()}{abbreviation}")

        #This filters through possible piece moves and removes values that are not valid
        possible_piece_moves = [
            move for move in possible_piece_moves  # loop through each move
            if not move.lower().startswith("xx")  # keep if it doesn't start with xx
            and move.lower() in phoenix.get_legal_piece_moves(get_turn_color(), position_dict=position_dict, all_moves=all_moves)  # keep if it's legal
            and len(move) != 2  # keep if it's not just 2 characters
        ]
        # input(f"phoenix.get_legal_piece_moves(...): {phoenix.get_legal_piece_moves(get_turn_color(), position_dict=position_dict, all_moves=all_moves)}")
        # input(f"possible_piece_moves: {possible_piece_moves}")
        # input(phoenix.get_legal_en_passant_moves(color=get_turn_color(), position_dict=position_dict, all_moves=all_moves))

        promotion_count = sum(1 for move in possible_piece_moves if len(move) == 5)
        #what if this promotion could result in check?
        if promotion_count == 4:
            if phoenix.is_king_in_check(get_turn_color(), test_move = possible_piece_moves[0], position_dict=position_dict, all_moves=all_moves): 
                return f"{get_turn_color()} king would be in check after {possible_piece_moves[0][:4]} promotion, please try again.", False
            else:
                return f"{possible_piece_moves[0][:4]}{ask_pawn_promotion()}", True
        elif promotion_count > 4:
            #remove moves that would result in check
            possible_piece_moves = [
                move for move in possible_piece_moves  # loop through each move
                if not phoenix.is_king_in_check(get_turn_color(), test_move = move, position_dict=position_dict, all_moves=all_moves)
            ]

            if len(possible_piece_moves) == 4:
                return f"{possible_piece_moves[0][:4]}{ask_pawn_promotion()}", True
            
            #multiple pawns can be promoted to same square, clarify which one
            elif len(possible_piece_moves) > 4:
                return f"{clarify_which_piece(wanted_position)}{wanted_position.lower()}{ask_pawn_promotion()}", True
            else:
                return f"{get_turn_color()} king would be in check after this pawn promotion, please try again.", False
        
        if len(possible_piece_moves) == 1:
            #check if in check after
                #if in check after, present check error message
                if phoenix.is_king_in_check(get_turn_color(), test_move = possible_piece_moves[0], position_dict=position_dict, all_moves=all_moves): 
                    return f"{get_turn_color()} king would be in check after {possible_piece_moves[0]}, please try again.", False
                else: #else do the move
                    return f"{possible_piece_moves[0]}", True

        elif len(possible_piece_moves) == 0:
            return "Move not found, please try again", False
        else:
            #more than one, sort through how many result in check
            possible_piece_moves = [
                move for move in possible_piece_moves  # loop through each move
                if not phoenix.is_king_in_check(get_turn_color(), test_move = move, position_dict=position_dict, all_moves=all_moves)
            ]

            #if more than one legal, clarify which
            if len(possible_piece_moves) > 1: 
                return f"{clarify_which_piece(wanted_position)}{wanted_position.lower()}", True
            #elif if one legal, do it
            elif len(possible_piece_moves) == 1: 
                return f"{possible_piece_moves[0]}", True
            #if none legal, present check error message
            else:
                return f"{get_turn_color()} king would be in check after this move, please try again.", False
    else: return "Move not found, please try again.", False

#used when more than one piece of the same type can move to the same square, to clarify which one to move
def clarify_which_piece(wanted_position):
    clarified_words = input("Please clarify which piece you would like to move: ")
    square = check_square(clarified_words)
    while True:
        if square:
            if wanted_position[-1] in ["1", "8"]:
                if f"{square.lower()}{wanted_position.lower()}q" in phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves):
                    return square.lower()
                elif f"{square.lower()}{wanted_position.lower()}" in phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves):
                    return square.lower()
                else: 
                    clarified_words = input("Sorry, I didn't get that. Please clarify which piece you would like to move: ")
                    square = check_square(clarified_words)
            else:
                if f"{square.lower()}{wanted_position.lower()}" in phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves):
                    return square.lower()
                else:
                    clarified_words = input("Sorry, I didn't get that. Please clarify which piece you would like to move: ")
                    square = check_square(clarified_words)
        else: 
            clarified_words = input("Sorry, I didn't get that. Please clarify which piece you would like to move: ")
            square = check_square(clarified_words)

#used to ask what the user wants to promote their pawn to
def ask_pawn_promotion():
    #  if piece == "pawn" and (wanted_position[-1] == "8" or wanted_position[-1] == "1"):
    promoted = input("What would you like to promote the pawn to?: ")
    while True:
        found_piece = check_for_pieces(promoted)
        if found_piece and found_piece != "pawn" and found_piece != "king": 
            if found_piece == "knight":
                promoted_symbol = "n"
            else:
                promoted_symbol = found_piece[0]
            break
        else: 
            promoted = input("Sorry, I didn't get that. Would you like to promote the pawn to?: ")
    return promoted_symbol

#used to remove everything before the wake word
def remove_before_word(text, word):
    parts = text.split(word, 1)  # Split at the first occurrence of the word
    return parts[1] if len(parts) > 1 else text  # Return everything after the word

#check intentions in a string
#used by process words
def check_intentions(text):
    text = text.lower()
    intent_counts = {intent: 0 for intent in intents}

    # Check each intent's phrases using regex with word boundaries.
    for intent, phrases in intents.items():
        # Sort phrases by length (longest first) to prioritize more specific phrases.
        for phrase in sorted(phrases, key=len, reverse=True):
            # Build a regex pattern to match the phrase as a separate token.
            pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
            if re.search(pattern, text):
                intent_counts[intent] += 1
                # Once a phrase from an intent is found, break out of the loop to avoid double-counting
                break
            
    # Choose the intent with the highest count.
    best_intent = max(intent_counts, key=intent_counts.get)
    if intent_counts[best_intent] > 0:
        return best_intent
    return False

def check_confirmation_response(text):
    text = text.lower()
    match_counts = {response_type: 0 for response_type in confirmation_responses}

    for response_type, phrases in confirmation_responses.items():
        for phrase in sorted(phrases, key=len, reverse=True):
            pattern = r'\b' + re.escape(phrase) + r'\b'
            if re.search(pattern, text):
                match_counts[response_type] += 1
                break  # Stop after first match for this type

    best_match = max(match_counts, key=match_counts.get)
    return best_match if match_counts[best_match] > 0 else False

def implement_intention(intention, computer_color=""):
    if intention == "undo": undo_last_move()
    elif intention == "restart": restart_game()
    elif intention == "takeover": computer_takeover(computer_color)
    else: return

def computer_takeover(color): pass

#####this was the original function, commented for reference
# import copy
# def get_moves_tree(depth, turn, position_dict, all_moves, board_positions_list):
#     print(f"still going {depth}.....")
#     move_dict = {}
#     leaf_list = []
    
#     # Get the possible moves for the current turn
#     possible_moves = phoenix.get_possible_moves(turn=phoenix.phoenix_get_turn_from_moves(all_moves), position_dict=position_dict, all_moves=all_moves)

#     # If no moves are possible, return "???"
#     if not possible_moves:
#         return "???"
    
#     for move in possible_moves:
#         # Make deep copies to preserve original state across recursive calls
#         new_position_dict = copy.deepcopy(position_dict)
#         new_all_moves = copy.deepcopy(all_moves)
#         new_board_positions_list = copy.deepcopy(board_positions_list)
#         new_turn = turn  # If turn is a simple variable (e.g., 'w' or 'b'), no deepcopy is needed
        
        
#         # Get the piece on the square for the current move
#         whole_piece = phoenix.get_what_is_on_square_specific(move[:2], position_dict=new_position_dict)
        
#         piece = check_for_pieces(whole_piece)
#         # Apply the move and update the board state
#         new_position_dict, new_all_moves, new_turn, new_board_positions_list = phoenix.implement_command(
#             move, piece, position_dict=new_position_dict, all_moves=new_all_moves, board_positions_list=new_board_positions_list
#         )
        
#         # If there is still depth left, recurse to generate the tree further
#         if depth > 0:
#             move_dict[move] = get_moves_tree(depth - 1, new_turn, new_position_dict, new_all_moves, new_board_positions_list)
#         else:
#             # If at leaf level, add the move to the leaf list
#             leaf_list.append(move)
    
#     # If we have any leaf nodes, return them
#     if leaf_list:
#         return leaf_list
#     else:
#         return move_dict

import copy

def get_best_move(depth, turn, position_dict, all_moves, board_positions_list, alpha, beta, maximizing_player):
    if depth == 0:
        return None, phoenix.evaluate_postion(position_dict)

    possible_moves = phoenix.get_possible_moves(turn=phoenix.phoenix_get_turn_from_moves(all_moves), position_dict=position_dict, all_moves=all_moves)

    if not possible_moves:
        return None, phoenix.evaluate_postion(position_dict)

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in possible_moves:
            # Deep copies
            new_position_dict = copy.deepcopy(position_dict)
            new_all_moves = copy.deepcopy(all_moves)
            new_board_positions_list = copy.deepcopy(board_positions_list)
            new_turn = turn

            # Get the piece and apply the move
            whole_piece = phoenix.get_what_is_on_square_specific(move[:2], position_dict=new_position_dict)
            piece = check_for_pieces(whole_piece)
            new_position_dict, new_all_moves, new_turn, new_board_positions_list = phoenix.implement_command(
                move, piece, position_dict=new_position_dict, all_moves=new_all_moves, board_positions_list=new_board_positions_list
            )

            # Recurse
            _, eval = get_best_move(depth - 1, new_turn, new_position_dict, new_all_moves, new_board_positions_list, alpha, beta, False)

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff

        return best_move, max_eval

    else:
        min_eval = float('inf')
        for move in possible_moves:
            # Deep copies
            new_position_dict = copy.deepcopy(position_dict)
            new_all_moves = copy.deepcopy(all_moves)
            new_board_positions_list = copy.deepcopy(board_positions_list)
            new_turn = turn

            # Get the piece and apply the move
            whole_piece = phoenix.get_what_is_on_square_specific(move[:2], position_dict=new_position_dict)
            piece = check_for_pieces(whole_piece)
            new_position_dict, new_all_moves, new_turn, new_board_positions_list = phoenix.implement_command(
                move, piece, position_dict=new_position_dict, all_moves=new_all_moves, board_positions_list=new_board_positions_list
            )

            # Recurse
            _, eval = get_best_move(depth - 1, new_turn, new_position_dict, new_all_moves, new_board_positions_list, alpha, beta, True)

            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff

        return best_move, min_eval



def print_tree(tree, indent=0, parent_has_more=False):
    if isinstance(tree, dict):
        keys = list(tree.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = '└─ ' if is_last else '├─ '
            print(('│  ' if parent_has_more else '   ') * indent + connector + str(key))
            print_tree(tree[key], indent + 1, not is_last)
    elif isinstance(tree, list):
        for i, item in enumerate(tree):
            is_last = (i == len(tree) - 1)
            connector = '└─ ' if is_last else '├─ '
            print(('│  ' if parent_has_more else '   ') * indent + connector + str(item))


def print_intention(intention, possible=True, computer_color=""):
    if intention == "undo":
        if possible: print("Undoing the last move.")
        else: print("No move to undo.")
    elif intention == "start":
        if possible: print("Starting a new game. (Logic not yet created)")
        else: print("Game is already in progress.")
    elif intention == "restart":
        if possible: print("Restarting the game.")
        else: print("Game is already in starting position.")
    elif intention == "end":
        if possible: print("Ending the game. (Logic not yet created)")
        else: print("Game is already in starting position.")
    elif intention == "takeover":
        if possible: print(f"{computer_color} will be taken over by the computer (when there is one, the logic isn't created)")
        else: print("Game has already been taken over.")
    elif intention == "list":
        print(f"{intention} intention logic not yet created.")
    else: print(f"{intention} intention logic not recognized.")

def is_intention_possible(intention):
    # undo, start, restart, end, takeover, list
    if intention == "undo": return True if all_moves else False
    elif intention == "start": return False if all_moves else True
    elif intention == "restart": return True if all_moves else False
    elif intention == "end": return True
    elif intention == "takeover": return True
    elif intention == "list": return True
    else: return False
 
#logic to undo the last move in all moves. used by implement_intention
def undo_last_move():
    global position_dict, all_moves, board_positions_list, global_turn
    #Can't undo a move if there aren't any to undo
    if not all_moves: return
    position_dict_temp = position_dict.copy()
    for piece, position in position_dict_temp.items():
        position_dict[piece] == ""
        #remove promoted pieces from the dictionary
        if "promoted" in piece.lower() and "pawn" not in piece.lower(): position_dict.pop(piece, None) 

    #set initial board position
    board_positions_list.clear()
    all_moves.pop()
    reset_global_turn()
    set_initials()

def restart_game():
    global position_dict, all_moves, board_positions_list
    if not all_moves: return
    position_dict_temp = position_dict.copy()
    for piece, position in position_dict_temp.items():
        position_dict[piece] == ""
        #remove promoted pieces from the dictionary
        if "promoted" in piece.lower() and "pawn" not in piece.lower(): position_dict.pop(piece, None) 
    locate_pieces_initial()
    reset_50_move_logic()
    board_positions_list.clear()
    board_positions_list.append(get_initial_board_position())
    all_moves.clear()
    reset_global_turn()

def get_confirm_message(intention):
    if intention == "undo": return f"Are you sure you want to undo the last move? This can not be undone. "
    elif intention == "start": return "" #no confirmation needed
    elif intention == "restart": return "Are you sure you want to restart the game? This can not be undone. "
    elif intention == "end": return "Are you sure you want to end the game? This can not be undone. "
    elif intention == "takeover": return f"Are you sure you want a computer to take over this game? "
    elif intention == "list": "" #no confirmation needed
    else: return ""

def process_intention(intention_check):
    intention_possible = is_intention_possible(intention_check)
    intention_message = get_confirm_message(intention_check)
    
    def execute_intention(do_intention=False, do_print_intention=False, cancel_intention=False, confirmation_not_clear=False, computer_takeover = False):
        computer_color = ""
        if computer_takeover: computer_color = input("What color would you like the computer to take over for? (Logic not yet created) ")
        if do_intention: implement_intention(intention_check, computer_color=computer_color)
        clear_screen() #do always
        print_board_visiual() #do always
        if do_print_intention: print_intention(intention_check, possible=intention_possible, computer_color=computer_color)
        if cancel_intention: print(f"Canceling {intention_check} command.")
        if confirmation_not_clear: print("Sorry, I didn't get that. Please try again.")
        play_game_loop() #do always

    #if possible, see if it needs to be confirmed
    if intention_possible: 
        #if confirmation is needed
        if intention_message: 
            intention_confirmation = input(intention_message)
            response = check_confirmation_response(intention_confirmation)

            #if the user responds yes or no
            if response:
                #positive
                if response.lower() == "affirmative": 
                    if intention_check == "takeover": execute_intention(do_intention=True, do_print_intention=True, computer_takeover = True)
                    else: execute_intention(do_intention=True, do_print_intention=True)
                #negative
                else: execute_intention(cancel_intention=True)
            
            #confirmation wasn't clear
            else: execute_intention(confirmation_not_clear=True)
        
        #if possible but no confirmation needed
        else: execute_intention(do_intention=True, do_print_intention=True)
        
    #if not possible, print the error message in print_intention
    else: execute_intention(do_print_intention=True)

#The first board position. used to add to board positions list
def get_initial_board_position():
    return ['b1c3', 'b1a3', 'g1h3', 'g1f3', 'a2a3', 'a2a4', 'b2b3', 'b2b4', 
            'c2c3', 'c2c4', 'd2d3', 'd2d4', 'e2e3', 'e2e4', 'f2f3', 'f2f4', 'g2g3', 
            'g2g4', 'h2h3', 'h2h4', 'b8a6', 'b8c6', 'g8f6', 'g8h6', 'a7a6', 'a7a5', 
            'b7b6', 'b7b5', 'c7c6', 'c7c5', 'd7d6', 'd7d5', 'e7e6', 'e7e5', 'f7f6', 
            'f7f5', 'g7g6', 'g7g5', 'h7h6', 'h7h5', 'white']

#check for castles in a string
#used by process words
def check_for_castles(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    count = 0 #number of castle commands found
    castle_found = "" #the key to the dictionary

    #check every homonym in the dictionary
    for castle_move, homonym in castles.items():
        for word in homonym:
            if word in words:
                castle_found = castle_move
                count += 1

    #if there is only one, return the respective command phrase
    # else, no castles found            
    if count == 1:
        if castle_found == "Kingside":
            return f"Castle Kingside"
        elif castle_found == "Queenside":
            return f"Castle Queenside"
    else:
        return False

#check for pieces in a string
#used by process words
def check_for_pieces(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    count = 0
    found_piece = ""
    for piece, synonyms in pieces.items():
        if any(word in words.lower() for word in synonyms):
            # print(piece)  # Output: queen
            found_piece = piece
            count +=1

    if count == 1:
        return found_piece
    else:
        return False
    
#check for squares in a string
#used by process words
def check_square(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    inv_letter_count, word_search, square_letter = check_square_letter(words)

    if inv_letter_count == 1:
        square_number = check_square_number(words, word_search)
        if square_number:
            result = "".join([square_letter, square_number])
            return result
        else:
            return False
    elif inv_letter_count > 1:
        return False
    else:
        square_together = check_squares_together(words)
        if square_together:
            return square_together
        else:
            return False
        
#check for square letters in a string
#used by check_square
def check_square_letter(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    count = 0
    square_letter = ""
    word_search = ""
    for word1 in words.lower().split(): #go through each word in the input
        for letter, homonym in letter_squares_separate.items():
            for word2 in homonym:
                if word1 == word2:
                    word_search = word1
                    square_letter = letter
                    count += 1

    return count, word_search, square_letter

#check for square numbers in a string
#used by check_square
def check_square_number(words, square_letter):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    next_word = find_next_word(words, square_letter)
    for number, homonym in number_squares_separate.items():
        for word in homonym:
            if next_word == word:
                return number
    return False

#check for squares together in a string
#used by check_square
def check_squares_together(words):
    global moves_string, all_moves, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    count = 0
    square = ""
    for word1 in words.lower().split(): #go through each word in the input
        for Square, homonym in squares_together.items():
            for word2 in homonym:
                if word1 == word2:
                    square = Square
                    count += 1
    if count == 1:
        return square
    else:
        return False

#used by parse_word_command
def parse_castle_command(move):
    global all_moves, position_dict
    turn = get_turn_color()
    castle_moves = {
        ("white", "Castle Kingside"): "e1g1",
        ("black", "Castle Kingside"): "e8g8",
        ("white", "Castle Queenside"): "e1c1",
        ("black", "Castle Queenside"): "e8c8",
    }

    if move in ["Castle Kingside", "Castle Queenside"]:
        # if is_single_move_legal(castle_moves[(turn, move)]):
        if castle_moves[(turn, move)].lower() in phoenix.get_possible_moves(turn=get_turn_color(), position_dict=position_dict, all_moves=all_moves):
            return castle_moves[(turn, move)], True
        else: 
            return "Castle move not legal, please try again", False

#returns "white" or "black"
#used to know which piece type positions to scan
def get_turn_color():
    global global_turn
    return global_turn

#gets game messages based on the given intention. Not currently used.         
def get_game_message(intention_found):
    messages = {
        "start": "Starting the game...",
        "restart": "Restarting the game...",
        "undo": "Redoing the last move...",
        "end": "Ending the game..."
    }
    return messages.get(intention_found, "Unknown command")
    
#used by check_square_number to find the square number directly after the square letter
def find_next_word(words, target):
    words = words.lower().split()
    for i in range(len(words) - 1):  # Stop at second last word
        if words[i] == target.lower():
            return words[i + 1]  # Return the next word
    return False  # Return False if not found

if __name__ == "__main__":
    main()