#errors to fix:
    #FIXED: black always stays during a capture??
    #FIXED: If white pawn taken, position_dict not updated for removal. Causes problems when another piece wants to move to that position.
    #FIXED: Castling, position_dict not updated for moving the rook. Causes problems with the rook moving the rook. 
        #note: These scenarios are similar, in that all_moves is updated correctly, but position_dict is not. So it looks right, but it is not.
    #FIXED: Pawn capturing on last row not working. This is because there are multiple notations for promotion of a pawn, eg; 'f7g8r', 'f7g8q', 'f7g8b'
    #FIXED scenario: en passant: different + or - 1 for if it is black or white capturing
    #FIXED: Pawn updated as 'Piece.WHITE_PAWN5': '8q'. Need to update promoted pawns
    #FIXED: if loading in the moves before starting, the promoted pawns are not updated. 
    #FIXED: do_temp_capture trying to fix pinned queens scenario
    #FIXED: get_legal_capture_moves_pawns, not working for some reason
    #FIXED: pinned queens moves_string, doing queen to e5 says it puts black king in check
    #FIXED: Notify when the king is in check
    #FIXED: if king is in check by pawn promotion, not shown as check.
    #FIXED: Promoted pawns in legal moves
    #FIXED: Print the board, without stockfish!
    #FIXED: Castling command takes forever to load (was still using stockfish)
    #FIXED: Asks for pawn promotion piece, before checks if legal
    #FIXED: Notify when the game is over, either by checkmate or stalemate
    #FIXED: If more than one piece can move to the same square, we present an error, but there is no way of fixing it
    #FIXED: If king moves to a square it can't, but it woucld be in check in that square, it shows as check error message
    #FIXED: If there are multiple moves to be checked, (piece moves) and none of them are legal, the error message is generic instead of specific check message
    
    #scenario: Work with other commands, like take over, restart, undo, etc;
    #scenario: Make it so get_all_moves and get_legal_piece moves is only generated once per turn, and the functions access global variables instead of generating it again
    #scenario: Order the possible moves from least to best, so that it can be used by the computer

import re
import os
from collections import Counter

def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS/Linux
        os.system('clear')

# moves_string = ['e2e4'] #first move
# moves_string = ['e2e4', 'd7d5'] #second move
# moves_string = ['e2e4', 'd7d5', 'e4d5'] #third move
# moves_string = ['e2e4', 'f7f5', 'd2d3', 'f5e4', 'd1e2', 'e4d3', 'c2d3', 'e7e5', 'd3d4', 'd8e7', 'e2e5'] #pinned queens
# moves_string = ['e2e4', 'e7e6', 'f2f4', 'd8e7', 'f4f5', 'e6f5', 'e4e5', 'd7d5'] #pinned en passant
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5'] #about to do en passants
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'c2c4', 'f7f5', 'h2h3', 'a7a5', 'h3h4', 'a5a4', 'h4h5', 'g7g5', 'h5g6'] #en passant load (white did the en passant)
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2'] #pawns about to be promoted
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'h2h3', 'd3c2', 'f7g8r', 'c2b1q'] #promoted pawns load
# moves_string = ['e2e4', 'd7d5', 'g2g4', 'b7b5', 'd2d3', 'c7c6', 'c1h6', 'g7h6', 'd1f3', 'd8a5', 'c2c3', 
                # 'a5b4', 'f3f6', 'e7f6', 'g4g5', 'b4b2', 'e4e5', 'b2d2', 'e1d2', 'b5b4', 'e5e6', 'd5d4', 'g5g6', 
                # 'c6c5', 'b1a3', 'c5c4', 'd3c4', 'b4b3', 'g6g7', 'd4d3', 'e6e7', 'b3b2', 'd2e3', 'd3d2', 'a1c1'] #multiple pawns can be promoted to same square, or multiple pawns can be promoted to different squares
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 
                # 'c2c3', 'b7b5', 'a2a3', 'b5b4', 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2'] #pawn can't be promoted because it is pinned
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5'] #multiple pieces to same square
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1', 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e3c4'] #two pinned knights
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1', 
#                 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                 'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7'] #two knights can move two same square, but one is pinned
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 'e7e6', 'e2e1',
#                  'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                  'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7', 'd2d3', 'e7e6', 'h2h3', 'f8b4'] #two knights can move to same spot, but both are pinned from different directions
# moves_string = ['g1f3', 'b8c6', 'b1a3', 'g8h6', 'a3c4', 'h6f5', 'f3e5', 'c6d4', 'c4e3', 'd4e2', 'e1e2', 
#                 'e7e6', 'e2e1', 'h7h6', 'f1c4', 'h6h5', 'c4e6', 'd8e7', 'e6b3', 'a7a6', 'e5c4', 'e7e6', 
#                 'c4d6', 'e8e7', 'd6b5', 'e7e8', 'b5c3', 'e6e7', 'd2d3', 'e7e6', 'h2h3', 'f8b4', 
#                 'h3h4', 'e6f6', 'e3g4', 'f6e7', 'g4e5', 'd7d6'] #two nights are both pinned from different directions, but can't move to the same spot like the scenario above
# moves_string = ['e2e4', 'c7c6', 'e1e2', 'b8a6', 'e2f3', 'a6b8', 'f3g4', 'b8a6', 'g4h5', 'd8a5', 'e4e5', 'd7d5'] #illegal en passant (white king would be in check)
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4', 'e5e4', 'f2f4'] #illegal en passant (black king would be in check)
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4'] #illegal en passant (black king would be in check)
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4', 'a4a5', 'h2h4', 'e5e4', 'f2f4'] # same scenario as above, but no pinned pawns
# moves_string = ['e2e3', 'd7d6', 'b1c3', 'e8d7', 'c3b1', 'd7c6', 'b1c3', 'c6b6', 'c3b1', 'b6a5', 'e3e4', 'd6d5', 'e4d5', 'a5a4', 'g1h3', 'e7e5', 'h3g1', 'h7h6', 'd1g4', 'a4a5', 'h2h4', 'e5e4', 'f2f4'] # same scenario as above, but no pinned pawns
# moves_string = ['g1f3', 'g8f6', 'g2g4', 'g7g5', 'f1h3', 'f8h6', 'e1g1', 'e8g8'] #loaded castling
moves_string = ['g1f3', 'g8f6', 'g2g3', 'g7g6', 'f1h3', 'f8h6', 'c2c3', 'c7c6', 'd1b3', 'd8b6', 'd2d4', 'b8a6', 'c1f4', 'd7d5', 'b1a3', 'c8f5', 'b3d5'] #testing illegal castling scenarios. (Black: kingside: can queenside: can't, White: kingside: can queenside: can)
# moves_string = ['e2e3', 'b8a6', 'd1h5', 'g8h6', 'f1c4', 'h6g4',] #about to be four move checkmate, black is about to loose
# moves_string = ['g1h3', 'e7e6', 'b1a3', 'd8h4', 'a3b1', 'f8c5', 'h3g1'] #about to be four move checkmate, white is about to loose
# moves_string = ['g1f3', 'g8f6', 'f3g1', 'f6g8', 'g1f3', 'g8f6', 'f3g1'] #about to be a stalemate by repetition
# moves_string = ['g1f3', 'b8c6', 'g2g3', 'b7b6', 'f1h3', 'c8a6', 'b1c3', 'g8f6', 'f3g5', 'c6e5', 'g5f3', 'e5c6', 'f3g1', 'c6b8', 'c3b1', 'a6b7', 'b1c3', 'b7a6', 'g1f3'] #about to be a stalemate by repetition, with a bunch of moves inbetween (knight to c6)
# moves_string = ['g1f3', 'e7e6', 'f3g1', 'd8h4', 'g1f3', 'h4h2', 'f3g1', 'h2h1', 'g1h3', 'h1h3', 'g2g4', 'h3g4', 'f2f4', 'g4f4', 'd2d4', 'f4d4', 'c2c4', 'd4c4', 
#                 'b2b4', 'c4b4', 'd1d2', 'b4b1', 'd2d1', 'b1c1', 'a2a3', 'c1a3', 'e1f2', 'a3a1', 'f2g3', 'a1d1', 'g3h4', 'd1e2', 'h4h3', 'e2f1', 
#                 'h3h4', 'g7g6', 'h4g5', 'f1f2', 'g5g4', 'd7d5', 'g4h3', 'f2g1', 'h3h4'] #about to be stalemate, white king not in check but no white moves possible. (black pawn to e5 will cause this)
# moves_string =  ['e2e3', 'b8a6', 'd1g4', 'a6b8', 'g4g7', 'b8a6', 'g7h8', 'a6b8', 'h8h7', 'b8a6', 'h7g8', 
#                  'a6b8', 'g1f3', 'e7e6', 'f3g1', 'd8g5', 'g8g5', 'd7d5', 'g5d5', 'c7c5', 'd5c5', 'b7b6', 'c5b6', 
#                  'b8a6', 'b6a6', 'c8b7', 'a6b7', 'a7a6', 'b7a6', 'a8a7', 'a6a7', 'f7f5', 'a7c5', 'f8d6', 'c5d6', 
#                  'f5f4', 'd6f4', 'e6e5', 'f4e5', 'e8d8', 'f1b5', 'd8c8', 'e5d4', 'c8b8', 'b2b3', 'b8a8', 'c1a3', 
#                  'a8b8', 'a3c5', 'b8a8', 'b5a6', 'a8b8', 'c5a7', 'b8a8'] #about to be stalemate, black king not in check but no black moves possible. any move that does not protect the bishop on a7 will be stalemate
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'c2c3', 'b7b5', 'a2a3', 'b5b4', 
#                 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2', 'h7h5', 'd1e1', 'h5h4', 'g2g4', 'h4g3', 
#                 'h2h4', 'g3f2', 'h1h2', 'g7g6', 'e1d1', 'g6g5', 'g1f3', 'g5g4', 'f3e1'] #multiple pawns can be promoted to same square, but one of them is pinned
# moves_string = ['e2e4', 'd7d5', 'e4e5', 'd5d4', 'e5e6', 'd4d3', 'e6f7', 'e8d7', 'c2c3', 'b7b5', 'a2a3', 
#                 'b5b4', 'a3a4', 'b4c3', 'd2c3', 'd3d2', 'e1e2', 'h7h5', 'd1e1', 'h5h4', 'g2g4', 'h4g3', 
#                 'h2h4', 'g3f2', 'h1h2', 'g7g6', 'e1d1', 'g6g5', 'g1f3', 'g5g4', 'f3e1', 'd7d6', 'c3c4', 
#                 'd6e5', 'c4c5', 'e5d4', 'b2b3', 'd4d5', 'c1b2', 'd5e4', 'b2e5', 'e4d5', 'h2h3', 'd5e4', 
#                 'e5h2', 'e4d4', 'h2g1'] #multiple pawns can be promoted to same square, but both of them are pinned
# moves_string = [] #empty new game

#used to update the current list of moves made, and transitively the current position. Can be used in tandem with above set position to set a position before playing 
all_moves = moves_string
board_positions_list = []

#the abbreviations that are used in pawn promotions
abbreviation_dict = {
    "n": "knight",
    "r": "rook",
    "q": "queen",
    "p": "pawn",
    "b": "bishop",
    "k": "king"
}

#dictionary used to track all the piece positions. Keeps track of specific pieces of same type
position_dict = {
    'Piece.WHITE_KING': "",
    'Piece.WHITE_QUEEN': "",
    'Piece.WHITE_BISHOP1': "",
    'Piece.WHITE_BISHOP2': "",
    'Piece.WHITE_KNIGHT1': "",
    'Piece.WHITE_KNIGHT2': "",
    'Piece.WHITE_ROOK1': "",
    'Piece.WHITE_ROOK2': "",
    'Piece.WHITE_PAWN1': "",
    'Piece.WHITE_PAWN2': "",
    'Piece.WHITE_PAWN3': "",
    'Piece.WHITE_PAWN4': "",
    'Piece.WHITE_PAWN5': "",
    'Piece.WHITE_PAWN6': "",
    'Piece.WHITE_PAWN7': "",
    'Piece.WHITE_PAWN8': "",
    
    'Piece.PROMOTED_WHITE_PAWN1': "",
    'Piece.PROMOTED_WHITE_PAWN2': "",
    'Piece.PROMOTED_WHITE_PAWN3': "",
    'Piece.PROMOTED_WHITE_PAWN4': "",
    'Piece.PROMOTED_WHITE_PAWN5': "",
    'Piece.PROMOTED_WHITE_PAWN6': "",
    'Piece.PROMOTED_WHITE_PAWN7': "",
    'Piece.PROMOTED_WHITE_PAWN8': "",


    'Piece.BLACK_KING': "",
    'Piece.BLACK_QUEEN': "",
    'Piece.BLACK_BISHOP1': "",
    'Piece.BLACK_BISHOP2': "",
    'Piece.BLACK_KNIGHT1': "",
    'Piece.BLACK_KNIGHT2': "",
    'Piece.BLACK_ROOK1': "",
    'Piece.BLACK_ROOK2': "",
    'Piece.BLACK_PAWN1': "",
    'Piece.BLACK_PAWN2': "",
    'Piece.BLACK_PAWN3': "",
    'Piece.BLACK_PAWN4': "",
    'Piece.BLACK_PAWN5': "",
    'Piece.BLACK_PAWN6': "",
    'Piece.BLACK_PAWN7': "",
    'Piece.BLACK_PAWN8': "",
    
    'Piece.PROMOTED_BLACK_PAWN1': "",
    'Piece.PROMOTED_BLACK_PAWN2': "",
    'Piece.PROMOTED_BLACK_PAWN3': "",
    'Piece.PROMOTED_BLACK_PAWN4': "",
    'Piece.PROMOTED_BLACK_PAWN5': "",
    'Piece.PROMOTED_BLACK_PAWN6': "",
    'Piece.PROMOTED_BLACK_PAWN7': "",
    'Piece.PROMOTED_BLACK_PAWN8': "",
}

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
    "restart": ["restart", "reset the game", "reset the board", "start over", "play again", "retry", "begin again"],
    "start": ["start", "new game", "set the board", "set the bored"],
    "undo": ["undo", "redo", "go back", "reverse", "take back move", "previous move", 
        "step back", "revert", "undo last action", "back"],
    "end": ["end", "end game", "quit", "stop playing", "exit", "close game", 
        "game over", "finish game", "shut down", "resign"],
    "takeover": ["take over", "takeover", "replace"],
    "list": ["list", "list commands", "options"]
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
global_turn = "White"

first_time = True

#load in data from another game
def set_position(moves_string_list):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    moves = moves_string_list.copy()  #shallow copy of the list
    castle_moves_list = ["e1g1", "e1c1", "e8g8", "e8c8"]
    castle_data = {
        "e1g1": "Castle Kingside",
        "e8g8": "Castle Kingside",
        "e1c1": "Castle Queenside",
        "e8c8": "Castle Queenside"
    }
    
    loaded_last_move = ""
    for move in moves:
        #remember loading pawn promotions
        if len(move) == 5:
            piece = abbreviation_dict[move[-1].lower()]
            implement_command(move, piece, update=False, loaded_last_move=loaded_last_move)
        
        #remember loading castling
        elif move in castle_moves_list: implement_command(move, castle_data[move], update=False, loaded_last_move=loaded_last_move)

        #everthing else
        else: implement_command(move, "fluff", update=False, loaded_last_move=loaded_last_move) #implement command ("fluff") doesn't actually use this unless it is for castling. need to fix that.
        loaded_last_move = move

#print all the moves that have occurred so far
def print_all_moves():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    print(f"all_moves: {all_moves}")

#used to replace text in a string. Currently used for converting promoted pawns to their new piece type
def replace_text(text, word, replace):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    new_text = text.replace(word, replace)
    return new_text

#main
def main():
    set_initials()
    play_game()

#the game loop
def play_game():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if first_time:
        words = input(f"Hello and welcome to the world of magic chess! My name is Phoenix. You can resume a recent game or start a new game. {get_turn_color()} to move, please state a command: ")
        first_time = False
    else: words = input(f"{get_turn_color()} to move. Please state a command: ")
    
    if words == "all moves":
        print_all_moves()
        play_game()
    elif words.lower() == "position dict":
        print(position_dict)
        play_game()
    elif words.lower() == "possible moves":
        print(get_possible_moves())
        play_game()
    elif words.lower() == "board positions list":
        print_board_positions()
        play_game()
    
    if check_intentions(words): 
        print(check_intentions(words))
        input()

    #decipher the command out of the words
    #if the move isn't possible, then the command is the error message
    (command, possible), piece = decipher_command(words)

    if possible: implement_command(command, piece)

    # input("press enter")
    clear_screen()
    print_board_visiual()

    #if there are no available moves for the person that did not just make a move in this function (aka whose turn it is), then it is either a checkmate or a stalemate
    if len(get_possible_moves()) == 0:
        if is_king_in_check(get_turn_color()): print(f"Game over, {'black' if get_turn_color().lower() == 'white' else 'white'} wins by checkmate")
        else: print(f"Game over by stalemate. {get_turn_color().lower()} doesn't have any legal moves.")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()

    # print(f"check_for_repetition_draw(): {check_for_repetition_draw()}")
    if check_for_repetition_draw():
        print(f"Game over - stalemate by repetition")
        print("Thanks for playing, play again soon! \n-Pheonix")
        exit()


    #print (or say) the command
    print(command)
    if is_king_in_check(get_turn_color()): print(f"{get_turn_color()} king is in check")

    if words != "quit":
        play_game()
    else:
        print("Thanks for playing, play again soon! \n-Pheonix")

#can also be used to test things before the game starts
def set_initials():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    locate_pieces_initial()
    board_positions_list.append(get_possible_moves(get_turn_color()) + get_possible_moves(get_opposite_turn_color()) + [get_turn_color()])
    set_position(moves_string)
    get_color_turn_initial()
    clear_screen()
    print_board_visiual()

#it is white if there have been no moves, otherwise count the moves_string
def get_color_turn_initial():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if len(moves_string) > 0: global_turn = "Black" if len(moves_string) % 2 == 1 else "White"
    else: global_turn = "White"

#change the turn color from White to Black, and from Black to White
def toggle_turn_color():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    global_turn = "Black" if global_turn == "White" else "White"

#Locates all of the initial pieces' positions, and puts them in the positions dictionary
def locate_pieces_initial():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    position_dict_temp = {
        'Piece.WHITE_KING': 'e1', 
        'Piece.WHITE_QUEEN': 'd1', 
        'Piece.WHITE_BISHOP1': 'c1', 
        'Piece.WHITE_BISHOP2': 'f1', 
        'Piece.WHITE_KNIGHT1': 'b1', 
        'Piece.WHITE_KNIGHT2': 'g1', 
        'Piece.WHITE_ROOK1': 'a1', 
        'Piece.WHITE_ROOK2': 'h1', 
        'Piece.WHITE_PAWN1': 'a2', 
        'Piece.WHITE_PAWN2': 'b2', 
        'Piece.WHITE_PAWN3': 'c2', 
        'Piece.WHITE_PAWN4': 'd2', 
        'Piece.WHITE_PAWN5': 'e2', 
        'Piece.WHITE_PAWN6': 'f2', 
        'Piece.WHITE_PAWN7': 'g2', 
        'Piece.WHITE_PAWN8': 'h2', 
        'Piece.BLACK_KING': 'e8', 
        'Piece.BLACK_QUEEN': 'd8', 
        'Piece.BLACK_BISHOP1': 'c8', 
        'Piece.BLACK_BISHOP2': 'f8', 
        'Piece.BLACK_KNIGHT1': 'b8', 
        'Piece.BLACK_KNIGHT2': 'g8', 
        'Piece.BLACK_ROOK1': 'a8', 
        'Piece.BLACK_ROOK2': 'h8', 
        'Piece.BLACK_PAWN1': 'a7', 
        'Piece.BLACK_PAWN2': 'b7', 
        'Piece.BLACK_PAWN3': 'c7', 
        'Piece.BLACK_PAWN4': 'd7', 
        'Piece.BLACK_PAWN5': 'e7', 
        'Piece.BLACK_PAWN6': 'f7', 
        'Piece.BLACK_PAWN7': 'g7', 
        'Piece.BLACK_PAWN8': 'h7'
        }
    
    for temp, position in position_dict_temp.items():
        position_dict[temp] = position

def change_promoted_pawn(promoted_pawn, current_move):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    position_dict[replace_text(promoted_pawn, "PAWN", abbreviation_dict[current_move[-1]].upper())] = position_dict.pop(promoted_pawn)

#pring position dict for debugging
def print_position_dict_debugging():
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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

#used for debugging the board positions list
def print_board_positions():
    global board_positions_list
    # Convert each inner list to a tuple so it can be counted
    hashable_positions = [tuple(position) for position in board_positions_list]
    counts = Counter(hashable_positions)
    for list, count in counts.items():
        print(f"{list}: {count}\n")

#if it is a legal piece move, and it doesn't result in a check afterwards, whether in check already or moving into it
#turn is an optional variable that allows you to look at the other player's possible moves as well. 
#It is used to update the board_positions_dict to scan for repeated board positions for a draw
#TODO
def get_possible_moves(turn=""):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if not turn:
        legal_piece_moves = get_legal_piece_moves(get_turn_color())
        legal_piece_moves = [
            move for move in get_legal_piece_moves(get_turn_color())
            if not is_king_in_check(get_turn_color(), test_move=move)
        ]
    else: 
        legal_piece_moves = get_legal_piece_moves(turn)
        legal_piece_moves = [
            move for move in get_legal_piece_moves(turn)
            if not is_king_in_check(turn, test_move=move)
        ]
    return legal_piece_moves

#prints possibles moves, not currently used
def print_possible_moves():
    print(f"Possible moves: {get_possible_moves()}")

#process words and parse word command
def decipher_command(words): 
    command, piece, square = process_words(words)
    return parse_word_command(piece, square, command), piece

#decipher the command out of the given words
#command (e2e4), piece (pawn), square (e4) = process_words(words)
def process_words(words):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time

    #remove everything before phoenix
    words = remove_before_word(words, "phoenix")

    # #check if the words have phrases for an intention. If not, it is ignored and continues on.
    # intentions = check_intentions(words)
    # if intentions:
    #     #if there is an explicit intention, return it. Done with process_words
    #     return intentions, None, None

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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if piece is not None:
        possible_piece_moves = []
        found_piece = ""

        if command == "castle":
            return parse_castle_command(piece)

        piece_positions = piece_type_spaces(piece, get_turn_color())
        for position in piece_positions:
            possible_piece_moves.append(f"{position}{wanted_position.lower()}")
            if position and piece == "pawn" and ((wanted_position[-1] == "8" and position[1] == "7") or (wanted_position[-1] == "1" and position[1] == "2")):
                    for abbreviation, abbreviation_piece in abbreviation_dict.items():
                        if abbreviation not in ["k", "p"]:
                            possible_piece_moves.append(f"{position}{wanted_position.lower()}{abbreviation}")

        #This filters through possible piece moves and removes values that are not valid
        possible_piece_moves = [
            move for move in possible_piece_moves  # loop through each move
            if not move.lower().startswith("xx")  # keep if it doesn't start with xx
            and move.lower() in get_legal_piece_moves(get_turn_color())  # keep if it's legal
            and len(move) != 2  # keep if it's not just 2 characters
        ]

        promotion_count = sum(1 for move in possible_piece_moves if len(move) == 5)
        #what if this promotion could result in check?
        if promotion_count == 4:
            if is_king_in_check(get_turn_color(), test_move = possible_piece_moves[0]): 
                return f"{get_turn_color()} king would be in check after {possible_piece_moves[0][:4]} promotion, please try again.", False
            else:
                return f"{possible_piece_moves[0][:4]}{ask_pawn_promotion()}", True
        elif promotion_count > 4:
            #remove moves that would result in check
            possible_piece_moves = [
                move for move in possible_piece_moves  # loop through each move
                if not is_king_in_check(get_turn_color(), test_move = move)
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
                if is_king_in_check(get_turn_color(), test_move = possible_piece_moves[0]): 
                    return f"{get_turn_color()} king would be in check after {possible_piece_moves[0]}, please try again.", False
                else: #else do the move
                    return f"{possible_piece_moves[0]}", True

        elif len(possible_piece_moves) == 0:
            return "Move not found, please try again", False
        else:
            #more than one, sort through how many result in check
            possible_piece_moves = [
                move for move in possible_piece_moves  # loop through each move
                if not is_king_in_check(get_turn_color(), test_move = move)
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

#implement the command with the capture, and updating the piece positions before printing them again
def implement_command(command, piece, update=True, loaded_last_move=""):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if update: handle_capture(command)
    else: handle_capture(command, loading=True, loaded_last_move=loaded_last_move)

    if len(command) == 5: #if it is a pawn promotion
        update_promoted_pawn_position(command, piece)
    else: 
        update_piece_position(command[:2], command[-2:], piece) #piece is actually a command for castling. fix lingo later
    if update: update_position(command) #Update all moves
    toggle_turn_color()
    board_positions_list.append(get_possible_moves(get_turn_color()) + get_possible_moves(get_opposite_turn_color()) + [get_turn_color()])

#used when more than one piece of the same type can move to the same square, to clarify which one to move
def clarify_which_piece(wanted_position):
    clarified_words = input("Please clarify which piece you would like to move: ")
    square = check_square(clarified_words)
    while True:
        if square:
            if wanted_position[-1] in ["1", "8"]:
                if f"{square.lower()}{wanted_position.lower()}q" in get_possible_moves():
                    return square.lower()
                else: 
                    clarified_words = input("Sorry, I didn't get that. Please clarify which piece you would like to move: ")
                    square = check_square(clarified_words)
            else:
                if f"{square.lower()}{wanted_position.lower()}" in get_possible_moves():
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
def check_intentions(text):
    global intents
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

#check for castles in a string
#used by process words
def check_for_castles(words):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    next_word = find_next_word(words, square_letter)
    for number, homonym in number_squares_separate.items():
        for word in homonym:
            if next_word == word:
                return number
    return False

#check for squares together in a string
#used by check_square
def check_squares_together(words):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
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

#used to find the positions of a desired piece type
#example: returns all the positions of the black pawns
def piece_type_spaces(wanted_piece, color):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    piece_positions = []
    for piece in position_dict:
        if ((wanted_piece.lower() in piece.lower()) and (color.lower() in piece.lower())):
            piece_positions.append(position_dict[piece])
            # print(f"{piece}: {position_dict[piece]}")
    return piece_positions

#get the name of the promoted pawn, given the regular pawn to be promoted 
def get_promoted_pawn(current_move):
    return "Piece.PROMOTED_" + get_turn_color().upper() + "_PAWN" + get_what_is_on_square_specific(current_move[:2])[-1]

#get the piece in the position dict that is on the given square
def get_what_is_on_square_specific(square):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    for key, val in position_dict.items():
        if val == square:
            return key
    return "None"

#update the position of a piece. The third parameter, command, is a bit confusing right now. it is only used for castling. also reffered to as piece in main
def update_piece_position(initial_position, new_position, command):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    turn = get_turn_color()
    rook_moves = {
        ("White", "Castle Kingside"): "h1f1",
        ("Black", "Castle Kingside"): "h8f8",
        ("White", "Castle Queenside"): "a1d1",
        ("Black", "Castle Queenside"): "a8d8",
    }

    for key, val in position_dict.items():
        if val == initial_position:
            position_dict[key] = new_position
            # print(f"{key} is now on {new_position}")

    if (turn, command) in rook_moves:
        update_piece_position(rook_moves[turn, command][:2], rook_moves[turn, command][-2:], "Rook move") #move the rook

def update_promoted_pawn_position(current_move, piece): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    promoted_pawn = get_promoted_pawn(current_move)
    position_dict[get_promoted_pawn(current_move)] = current_move[2:4]
    change_promoted_pawn(promoted_pawn, current_move)
    update_piece_position(current_move[:2], "xx", piece)

def update_piece_position_no_castles(initial_position, new_position):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    for key, val in position_dict.items():
        if val == initial_position:
            position_dict[key] = new_position

#used by parse_word_command
def parse_castle_command(move):
    turn = get_turn_color()
    castle_moves = {
        ("White", "Castle Kingside"): "e1g1",
        ("Black", "Castle Kingside"): "e8g8",
        ("White", "Castle Queenside"): "e1c1",
        ("Black", "Castle Queenside"): "e8c8",
    }

    if move in ["Castle Kingside", "Castle Queenside"]:
        if castle_moves[(turn, move)].lower() in get_possible_moves():
            return castle_moves[(turn, move)], True
        else: 
            return "Castle move not legal, please try again", False

#updates all moves with the current moves that have been made
#only called if not loading a game in implement_command 
def update_position(current_move):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    all_moves.append(current_move)

#returns "White" or "Black"
#used to know which piece type positions to scan
def get_turn_color():
    global global_turn
    return global_turn

#opposite of get_turn_color, get who's turn it is NOT
def get_opposite_turn_color():
    global global_turn
    opposite_color = "Black" if global_turn == "White" else "White"
    return opposite_color

#the position of pieces that are captured are "xx"
#works with normal captures and en passants
def handle_capture(move, loading=False, loaded_last_move=""):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if is_en_passant_move(move, loading=loading, loaded_last_move=loaded_last_move): update_piece_position((decrement_string if get_turn_color() == "White" else increment_string)(move[-2:]), "xx", "capture")
    else: 
        for key, val in position_dict.items():
            if len(move) == 5: 
                if move[2:4] == val: update_piece_position(move[2:4], "xx", "capture")
            else:
                if move[-2:] == val: update_piece_position(move[-2:], "xx", "capture")
    
#used by handle_capture for en passant pawn capture positions
def increment_string(s):
    return re.sub(r'(\d+)$', lambda x: str(int(x.group(1)) + 1), s)

#used by handle_capture for en passant pawn capture positions
def decrement_string(s):
    return re.sub(r'(\d+)$', lambda x: str(int(x.group(1)) - 1), s)

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

#see if the king is in check with the current position
def is_king_in_check(color, legal_king_threaten_moves_test_opposite = [], test_move = ""): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    removed_piece = "None"
    en_passant_removed_square = ""
    if test_move: 
        # print("824")
        if is_en_passant_move(test_move): 
            en_passant_removed_square = test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1))
            removed_piece = get_what_is_on_square_specific(en_passant_removed_square)
            # print(test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1)))
        else: removed_piece = get_what_is_on_square_specific(test_move[-2:])
        # print(f"removed_piece: {removed_piece}")
        # print(f"test_move: {test_move}")
        # print(f"test_move[-2:]: {test_move[-2:]}")
        if removed_piece != "None": 
            do_temp_capture(removed_piece)
            # print("829")
        update_piece_position_no_castles(test_move[:2], test_move[-2:])
    opposite_color = "black" if color.lower() == "white" else "white"
    king_positions = [king for king in piece_type_spaces("king", color) if (king and (king != "xx"))]  # Remove empty strings and xxs
    if not legal_king_threaten_moves_test_opposite: legal_king_threaten_moves_test_opposite = get_legal_king_threaten_moves(opposite_color)
    for move in legal_king_threaten_moves_test_opposite:
        for king in king_positions:
            if move[2:4] == king:
                if test_move: 
                    update_piece_position_no_castles(test_move[-2:], test_move[:2])
                    # print("838")
                if removed_piece != "None": 
                    # (test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1))) if is_en_passant_move(test_move) else test_move[:2]
                    undo_temp_capture(removed_piece, test_move[-2:], en_passant_removed_square)
                    # undo_temp_capture(removed_piece, (test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1))) if is_en_passant_move(test_move) else test_move[:2])
                    # print("841")
                return True
    if test_move: 
        update_piece_position_no_castles(test_move[-2:], test_move[:2])
        # print("845")
    if removed_piece != "None": 
        undo_temp_capture(removed_piece, test_move[-2:], en_passant_removed_square)
        # print((test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1))) if is_en_passant_move(test_move) else test_move[:2])
        # undo_temp_capture(removed_piece, (test_move[2] + chr(ord(test_move[3]) + (-1 if get_turn_color().lower() == "white" else 1))) if is_en_passant_move(test_move) else test_move[:2])
        # print("848")
    return False

def is_en_passant_move(given_move, loading = False, loaded_last_move = ""):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    color = get_turn_color()
    opposite_color = "black" if color.lower() == "white" else "white"
    potential_position = given_move[2:4]
    if not all_moves or len(given_move) != 4: return False
    last_move = all_moves[-1] if not loading else loaded_last_move
    en_passant_data = {
        "white": ("5", -1),
        "black": ("4", 1),
    }
    rank, direction = en_passant_data[color.lower()]
    moving_piece = get_what_is_on_square_specific(given_move[:2])
    removed_piece_position = potential_position[0] + chr(ord(potential_position[1]) + direction)
    removed_piece = get_what_is_on_square_specific(removed_piece_position).lower()

    checks = [
        not all_moves or len(given_move) != 4,
        "pawn" not in moving_piece.lower() or "promoted" in moving_piece.lower(),
        given_move[-1] != chr(ord(rank) - direction),
        "pawn" not in removed_piece or "promoted" in removed_piece or opposite_color not in removed_piece,
        last_move != removed_piece_position[0] + chr(ord(removed_piece_position[1]) + -2 * direction) + removed_piece_position,
    ]

    # Optional: labels to make debugging clearer
    check_descriptions = [
        "Empty move list or invalid move length",
        "Not a normal pawn or is a promoted piece",
        f"Move destination rank is wrong {given_move[-1]} does not equal {chr(ord(rank) - direction)}",
        f"Captured piece is not an enemy pawn or is promoted, {removed_piece}, removed_piece_position: {removed_piece_position}",
        f"Last move doesn't match expected en passant position, {last_move} is not {removed_piece_position[0] + chr(ord(removed_piece_position[1]) + -2 * direction) + removed_piece_position}"
    ]

    if any(checks): return False
    return True

def do_temp_capture(removed_piece):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    position_dict[removed_piece] = "xx"

def undo_temp_capture(removed_piece, square, en_passant_removed_square):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    if en_passant_removed_square: 
        position_dict[removed_piece] = en_passant_removed_square
        return
    position_dict[removed_piece] = square

#TODO
def get_legal_piece_moves(color):
    opposite_color = get_opposite_turn_color().lower()
    legal_king_threaten_moves_test = get_legal_king_threaten_moves(color)
    legal_king_threaten_moves_opposite = get_legal_king_threaten_moves(opposite_color)
    legal_moves = sum([
        legal_king_threaten_moves_test,
        get_legal_castle_moves(color, legal_king_threaten_moves_opposite) or [],
        get_legal_pawn_normal_moves(color) or [],
        get_legal_en_passant_moves(color) or [],
        get_legal_promoted_pawn_moves(color) or [],
    ], [])
    return legal_moves

def get_legal_king_threaten_moves(color):
    legal_king_threaten_moves_test = sum([
        get_legal_capture_moves_pawns(color),
        get_legal_rook_moves(color),
        get_legal_knight_moves(color),
        get_legal_bishop_moves(color),
        get_legal_queen_moves(color),
        get_legal_king_moves(color),
        get_legal_pawn_promotion_capture_moves(color)
    ], [])
    return legal_king_threaten_moves_test

def get_legal_pawn_promotion_capture_moves(color):
    legal_promoted_pawn_moves = get_legal_promoted_pawn_moves(color)
    legal_promoted_pawn_moves_copy = legal_promoted_pawn_moves
    for move in legal_promoted_pawn_moves_copy:
        if move[0] == move[2]: legal_promoted_pawn_moves.remove(move)
    return legal_promoted_pawn_moves

def get_legal_castle_moves(color, legal_capture_moves): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    legal_castle_moves = []
    castle_kingside = True
    castle_queenside = True
    king_positions = [king for king in piece_type_spaces("king", color) if (king and (king != "xx"))]  # Remove empty strings and xxs
    rook_positions = [rook for rook in piece_type_spaces("rook", color) if (rook and (rook != "xx"))]  # Remove empty strings and xxs

    castle_data = {
        "white": ("1", ["f1", "g1"], ["b1", "c1", "d1"], "e1g1", "e1c1", "h1", "a1"),
        "black": ("8", ["f8", "g8"], ["b8", "c8", "d8"], "e8g8", "e8c8", "h8", "a8"),
    }

    rank, kingside_squares, queenside_squares, kingside_castle, queenside_castle, kingside_rook, queenside_rook = castle_data[color.lower()]
    
    #rank is number, file is letter
    for king in king_positions:
        if king[0].lower() != "e":
            # print(f"{color} king not on e")
            return
        if king[1].lower() != rank:
            # print(f"{color} king not on correct rank")
            return
        
    for rook in rook_positions:
        if rook[0].lower() not in ("a", "h"):
            # print(f"{color} rook not on a or h")
            return
        if rook[1].lower() != rank:
            # print(f"{color} rook not correct rank")
            return
        
    for move in legal_capture_moves:
        if move[2:4] == f"e{rank}":
            # print(f"{color} king in check, can't castle at all")
            return #king in check, can't castle at all
        for square in kingside_squares:
            if move[2:4] == square:
                castle_kingside = False
                # print(f"{color} can't castle kingside, can't move into check")
                break #can't castle kingside, can't move into check
        for square in queenside_squares:
            if square.startswith("b"): continue  # skip this square entirely
            if move[2:4] == square:
                castle_queenside = False
                # print(f"{color} can't castle queenside, can't move into check")
                break #can't castle queenside, can't move into check

    for move in all_moves:
        if move[:2] == f"e{rank}":
            # print(f"{color} can't castle at all, king already moved")
            return
        if move[:2] == kingside_rook:
            # print(f"{color} can't castle kingside, rook already moved")
            castle_kingside = False
        if move[:2] == queenside_rook:
            # print(f"{color} can't castle queenside, rook already moved")
            castle_queenside = False

    if castle_kingside: 
        for square in kingside_squares:
            if get_what_is_on_square_specific(square) != "None":
                # print(f"{color} can't castle kingside, something is blocking")
                break  # Exit the loop immediately if a square is not "None"
        else: legal_castle_moves.append(kingside_castle)

    if castle_queenside: 
        for square in queenside_squares:
            if get_what_is_on_square_specific(square) != "None":
                # print(f"{color} can't castle queenside, something is blocking")
                break  # Exit the loop immediately if a square is not "None"
        else: legal_castle_moves.append(queenside_castle)

    # print (legal_castle_moves)
    return legal_castle_moves

def get_legal_en_passant_moves(color): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    legal_en_passant_moves = []
    if not all_moves:
        return
    last_move = all_moves[-1]
    pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
    en_passant_data = {
        "white": ("5", [(-1,1), (1, 1)]),
        "black": ("4", [(-1,-1), (1, -1)]),
    }

    rank, direction = en_passant_data[color.lower()]
    for pawn in pawn_positions:
        same_rank = pawn[1] == rank
        last_move_same_rank = last_move[3] == rank
        adjacent_file = last_move[2] in (chr(ord(pawn[0]) + 1), chr(ord(pawn[0]) - 1))
        if same_rank and last_move_same_rank and adjacent_file:
            from_square = pawn
            for sub_direction in direction:
                new_file = chr(ord(pawn[0]) + sub_direction[0])
                new_rank = int(pawn[1]) + sub_direction[1]

                if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                    to_square = f"{new_file}{new_rank}"
                    legal_en_passant_moves.append(from_square + to_square)

    # print(legal_en_passant_moves)
    return legal_en_passant_moves

#Pawns moving 1 and 2 spaces forward
def get_legal_pawn_normal_moves(color): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    legal_pawn_normal_moves = []
    pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
    # pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
    direction = [1,2] if color.lower() == "white" else [-1,-2]
    for pawn in pawn_positions:
        for offset in direction:
            new_rank = int(pawn[1]) + offset
            # if 1 <= new_rank <= 8:
            if (color.lower() == "white" and 1 <= new_rank <= 7) or (color.lower() == "black" and 2 <= new_rank <= 8):
                potential_position = f"{pawn[0]}{new_rank}"
                piece = get_what_is_on_square_specific(potential_position)
                if piece == "None" and color.lower() not in piece.lower():
                    legal_pawn_normal_moves.append(f"{pawn}{potential_position}")
                else: break

    return legal_pawn_normal_moves

#Pawns moving diagonal
def get_legal_capture_moves_pawns(color):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    #not doing enpassant, because this is for scanning for checks
    legal_pawn_capture_moves = []
    pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
    # pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
    # print(f"pawn positions: {pawn_positions}")
    direction = 1 if color.lower() == "white" else -1
    # print(f"position_dict: {position_dict}")
    for pawn in pawn_positions:
        for offset in [-1, 1]:  # Check left (-1) and right (+1) diagonals
            new_file = chr(ord(pawn[0]) + offset)
            new_rank = int(pawn[1]) + direction
            # print(f"pawn: {pawn}, new_file: {new_file}, new_rank: {new_rank}")
            if "a" <= new_file <= "h" and (color.lower() == "white" and 1 <= new_rank <= 7) or (color.lower() == "black" and 2 <= new_rank <= 8):
                potential_position = f"{new_file}{new_rank}"
                piece = get_what_is_on_square_specific(potential_position)
                # print(f"piece: {piece}, potential_position: {potential_position}")
                if piece != "None" and color.lower() not in piece.lower():
                    legal_pawn_capture_moves.append(f"{pawn}{potential_position}")
    # print(f"legal_pawn_capture_moves: {legal_pawn_capture_moves}")
    return legal_pawn_capture_moves

def get_legal_knight_moves(color):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    legal_knight_moves = []
    knight_positions = [knight for knight in piece_type_spaces("knight", color) if (knight and (knight != "xx") and not knight[-1].isalpha())]  # Remove empty strings and xxs
    directions = [(1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, 1), (2, -1)]  # (delta_file, delta_rank) for 8 knight positions
    for knight in knight_positions:
        for delta_file, delta_rank in directions:
            file, rank = knight[0], int(knight[1])
            file = chr(ord(file) + delta_file)
            rank += delta_rank
            potential_position = f"{file}{rank}"
            if 'a' <= file <= 'h' and 1 <= rank <= 8:
                piece = get_what_is_on_square_specific(potential_position)
                if color.lower() not in piece.lower():
                    legal_knight_moves.append(f"{knight}{potential_position}")
    # print(legal_knight_moves)     
    return legal_knight_moves     

def get_legal_bishop_moves(color): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    opposite_color = get_opposite_turn_color().lower()
    legal_bishop_capture_moves = []
    bishop_positions = [bishop for bishop in piece_type_spaces("bishop", color) if (bishop and (bishop != "xx") and not bishop[-1].isalpha())]  # Remove empty strings and xxs
    directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]  # (delta_file, delta_rank) for the four diagonals
    for bishop in bishop_positions:
        for delta_file, delta_rank in directions:
            file, rank = bishop[0], int(bishop[1])
            enemy_encountered = False

            while 'a' <= file <= 'h' and 1 <= rank <= 8:
                file = chr(ord(file) + delta_file)
                rank += delta_rank

                if not ('a' <= file <= 'h' and 1 <= rank <= 8):  
                    break  # Stop if out of bounds

                potential_position = f"{file}{rank}"
                piece = get_what_is_on_square_specific(potential_position)

                if piece == "None" and not enemy_encountered:
                    legal_bishop_capture_moves.append(f"{bishop}{potential_position}")

                elif opposite_color.lower() in piece.lower() and not enemy_encountered: 
                    legal_bishop_capture_moves.append(f"{bishop}{potential_position}")
                    enemy_encountered = True
                    
                else:
                    break  # Stop if blocked by own piece or after capturing an enemy

    return legal_bishop_capture_moves

def get_legal_rook_moves(color): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    opposite_color = get_opposite_turn_color().lower()
    legal_rook_capture_moves = []
    rook_positions = [rook for rook in piece_type_spaces("rook", color) if (rook and (rook != "xx") and not rook[-1].isalpha())]  # Remove empty strings and xxs
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # (delta_file, delta_rank) for up, down, right, left
    for rook in rook_positions:
        for delta_file, delta_rank in directions:
            file, rank = rook[0], int(rook[1])
            enemy_encountered = False

            while 'a' <= file <= 'h' and 1 <= rank <= 8:
                file = chr(ord(file) + delta_file)
                rank += delta_rank

                if not ('a' <= file <= 'h' and 1 <= rank <= 8):  
                    break  # Stop if out of bounds

                potential_position = f"{file}{rank}"
                piece = get_what_is_on_square_specific(potential_position)

                if piece == "None" and not enemy_encountered:
                    legal_rook_capture_moves.append(f"{rook}{potential_position}")

                elif opposite_color.lower() in piece.lower() and not enemy_encountered: 
                    legal_rook_capture_moves.append(f"{rook}{potential_position}")
                    enemy_encountered = True
                    
                else:
                    break  # Stop if blocked by own piece or after capturing an enemy

    return legal_rook_capture_moves

def get_legal_queen_moves(color): 
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    opposite_color = get_opposite_turn_color().lower()
    legal_queen_capture_moves = []
    queen_positions = [queen for queen in piece_type_spaces("queen", color) if (queen and (queen != "xx") and not queen[-1].isalpha())]  # Remove empty strings and xxs
    # print(f"{color} queen_postions: {queen_positions}")
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]  # (delta_file, delta_rank) for up, down, right, left, and diagonals
    for queen in queen_positions:
        for delta_file, delta_rank in directions:
            file, rank = queen[0], int(queen[1])
            enemy_encountered = False

            while 'a' <= file <= 'h' and 1 <= rank <= 8:
                file = chr(ord(file) + delta_file)
                rank += delta_rank

                if not ('a' <= file <= 'h' and 1 <= rank <= 8):  
                    break  # Stop if out of bounds

                potential_position = f"{file}{rank}"
                piece = get_what_is_on_square_specific(potential_position)
                # print(f"queen piece: {piece}")

                if piece == "None" and not enemy_encountered:
                    legal_queen_capture_moves.append(f"{queen}{potential_position}")

                elif opposite_color.lower() in piece.lower() and not enemy_encountered: 
                    legal_queen_capture_moves.append(f"{queen}{potential_position}")
                    enemy_encountered = True
                    
                else:
                    break  # Stop if blocked by own piece or after capturing an enemy

    # print(f"{color} legal_q`ueen_capture_moves: {legal_queen_capture_moves}")
    return legal_queen_capture_moves

def get_legal_king_moves(color):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    legal_king_moves = []
    king_positions = [king for king in piece_type_spaces("king", color) if (king and (king != "xx") and not king[-1].isalpha())]  # Remove empty strings and xxs
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]  # (delta_file, delta_rank) for up, down, right, left, and diagonals
    for king in king_positions:
        for delta_file, delta_rank in directions:
            file, rank = king[0], int(king[1])
            file = chr(ord(file) + delta_file)
            rank += delta_rank
            potential_position = f"{file}{rank}"
            if 'a' <= file <= 'h' and 1 <= rank <= 8:
                piece = get_what_is_on_square_specific(potential_position)
                if color.lower() not in piece.lower():
                    legal_king_moves.append(f"{king}{potential_position}")

    # print(f"{color} legal_king_moves: {legal_king_moves}")
    return legal_king_moves

def get_legal_promoted_pawn_moves(color):
    global moves_string, all_moves, abbreviation_dict, position_dict, symbols_dict, board_dict, pieces, intents, castles, letter_squares_separate, number_squares_separate, squares_together, global_turn, first_time
    #not doing enpassant, because this is for scanning for checks
    legal_pawn_promotion_moves = []
    pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
    # pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
    direction = 1 if color.lower() == "white" else -1
    for pawn in pawn_positions:
        for offset in [-1, 1, 0]:  # Check left (-1) and right (+1) diagonals
            new_file = chr(ord(pawn[0]) + offset)
            new_rank = int(pawn[1]) + direction
            # print(f"pawn: {pawn}, new_file: {new_file}, new_rank: {new_rank}")
            if "a" <= new_file <= "h" and ((color.lower() == "white" and new_rank == 8) or (color.lower() == "black" and new_rank == 1)):
                potential_position = f"{new_file}{new_rank}"
                piece = get_what_is_on_square_specific(potential_position)

                #moving straight forward allowed
                if offset == 0 and piece == "None":
                    for abbreviation in abbreviation_dict.items():
                        if abbreviation != "k" and abbreviation != "p":
                            legal_pawn_promotion_moves.append(f"{pawn}{potential_position}{abbreviation[0]}")

                #moving diagonal allowed
                if offset != 0 and piece != "None":
                    for abbreviation in abbreviation_dict.items():
                        if abbreviation != "k" and abbreviation != "p":
                            legal_pawn_promotion_moves.append(f"{pawn}{potential_position}{abbreviation[0]}")
    # print(legal_pawn_promotion_moves)
    return legal_pawn_promotion_moves

if __name__ == "__main__":
    main()