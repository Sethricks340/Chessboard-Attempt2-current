# Personal Hands-Off Entity for Navigating Interactive eXperiences: PHEONIX
import re
import os
import copy
from collections import Counter

class Phoenix:


    def __init__(self):
        self.abbreviation_dict = {
            "n": "knight",
            "r": "rook",
            "q": "queen",
            "p": "pawn",
            "b": "bishop",
            "k": "king"
        }

    #example function, while I am learning python syntax for classes
    def rev(self):
        print(f"'Vroom Vroom! I'm an engine!'")
        print(f"print {PST_reversed}")

    def get_legal_piece_moves(self, color, position_dict, all_moves):
        opposite_color = "black" if color.lower() == "white" else "white"
        # if position_dict is None: raise ValueError("position_dict is None in get_legal_piece_moves")
        legal_king_threaten_moves_test = self.get_legal_king_threaten_moves(color, position_dict=position_dict, all_moves=all_moves)
        legal_king_threaten_moves_opposite = self.get_legal_king_threaten_moves(opposite_color, position_dict=position_dict, all_moves=all_moves)
        legal_moves = sum([
            legal_king_threaten_moves_test,
            self.get_legal_castle_moves(color, legal_king_threaten_moves_opposite, position_dict=position_dict, all_moves=all_moves) or [],
            self.get_legal_pawn_normal_moves(color, position_dict=position_dict, all_moves=all_moves) or [],
            self.get_legal_en_passant_moves(color, position_dict=position_dict, all_moves=all_moves) or [],
            self.get_legal_promoted_pawn_moves(color, position_dict=position_dict, all_moves=all_moves) or [],
        ], [])
        return legal_moves
    
    def get_possible_moves(self, turn, position_dict, all_moves):
        # if position_dict is None: raise ValueError("position_dict is None in get_possible_moves")
        legal_piece_moves = self.get_legal_piece_moves(turn, position_dict=position_dict, all_moves=all_moves)
        legal_piece_moves = [
            move for move in self.get_legal_piece_moves(turn, position_dict=position_dict, all_moves=all_moves)
            if not self.is_king_in_check(turn, test_move=move, position_dict=position_dict, all_moves=all_moves)
        ]
        return legal_piece_moves
    
    def get_legal_king_threaten_moves(self, color, position_dict, all_moves):
        # if position_dict is None: raise ValueError("position_dict is None in get_legal_king_threaten_moves")
        legal_king_threaten_moves_test = sum([
            self.get_legal_capture_moves_pawns(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_rook_moves(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_knight_moves(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_bishop_moves(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_queen_moves(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_king_moves(color, position_dict=position_dict, all_moves=all_moves),
            self.get_legal_pawn_promotion_capture_moves(color, position_dict=position_dict, all_moves=all_moves)
        ], [])
        return legal_king_threaten_moves_test
    
    def update_piece_position_no_castles(self, initial_position, new_position, position_dict):
        for key, val in position_dict.items():
            if val == initial_position:
                position_dict[key] = new_position

    def is_king_in_check(self, color, position_dict, all_moves, legal_king_threaten_moves_test_opposite = [], test_move = ""):
        removed_piece = "None"
        en_passant_removed_square = ""
        if test_move: 
            if self.is_en_passant_move(test_move, turn_color=color, position_dict=position_dict, all_moves=all_moves): 
                en_passant_removed_square = test_move[2] + chr(ord(test_move[3]) + (-1 if color.lower() == "white" else 1))
                removed_piece = self.get_what_is_on_square_specific(en_passant_removed_square, position_dict=position_dict)
            else: removed_piece = self.get_what_is_on_square_specific(test_move[-2:], position_dict=position_dict)
            if removed_piece != "None": 
                self.do_temp_capture(removed_piece, position_dict, all_moves)
            self.update_piece_position_no_castles(initial_position=test_move[:2], new_position=test_move[-2:], position_dict=position_dict)
        opposite_color = "black" if color.lower() == "white" else "white"
        king_positions = [king for king in self.piece_type_spaces("king", color, position_dict=position_dict, all_moves=all_moves) if (king and (king != "xx"))]  # Remove empty strings and xxs
        if not legal_king_threaten_moves_test_opposite: legal_king_threaten_moves_test_opposite = self.get_legal_king_threaten_moves(opposite_color, position_dict=position_dict, all_moves=all_moves)
        for move in legal_king_threaten_moves_test_opposite:
            for king in king_positions:
                if move[2:4] == king:
                    if test_move: 
                        self.update_piece_position_no_castles(test_move[-2:], test_move[:2], position_dict=position_dict)
                    if removed_piece != "None": 
                        self.undo_temp_capture(removed_piece, test_move[-2:], en_passant_removed_square, position_dict=position_dict, all_moves=all_moves)
                    return True
        if test_move: 
            self.update_piece_position_no_castles(test_move[-2:], test_move[:2], position_dict=position_dict)
        if removed_piece != "None": 
            self.undo_temp_capture(removed_piece, test_move[-2:], en_passant_removed_square, position_dict=position_dict, all_moves=all_moves)
        return False

    # #Pawns moving diagonal
    def get_legal_capture_moves_pawns(self, color, position_dict, all_moves):
        legal_pawn_capture_moves = []
        # if position_dict is None: raise ValueError("position_dict is None in get_legal_capture_moves_pawns")
        pawn_positions = [pawn for pawn in self.piece_type_spaces("pawn", color, position_dict=position_dict, all_moves=all_moves) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
        direction = 1 if color.lower() == "white" else -1
        for pawn in pawn_positions:
            for offset in [-1, 1]:  # Check left (-1) and right (+1) diagonals
                new_file = chr(ord(pawn[0]) + offset)
                new_rank = int(pawn[1]) + direction
                if "a" <= new_file <= "h" and (color.lower() == "white" and 1 <= new_rank <= 7) or (color.lower() == "black" and 2 <= new_rank <= 8):
                    potential_position = f"{new_file}{new_rank}"
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)
                    if piece != "None" and color.lower() not in piece.lower():
                        legal_pawn_capture_moves.append(f"{pawn}{potential_position}")
        return legal_pawn_capture_moves

    def get_legal_pawn_promotion_capture_moves(self, color, position_dict, all_moves):
        legal_promoted_pawn_moves = self.get_legal_promoted_pawn_moves(color, position_dict=position_dict, all_moves=all_moves)
        legal_promoted_pawn_moves_copy = legal_promoted_pawn_moves
        for move in legal_promoted_pawn_moves_copy:
            if move[0] == move[2]: legal_promoted_pawn_moves.remove(move)
        return legal_promoted_pawn_moves

    def get_legal_castle_moves(self, color, legal_capture_moves, position_dict, all_moves): 
        legal_castle_moves = []
        castle_kingside = True
        castle_queenside = True
        king_positions = [king for king in self.piece_type_spaces("king", color, position_dict=position_dict, all_moves=all_moves) if (king and (king != "xx"))]  # Remove empty strings and xxs
        rook_positions = [rook for rook in self.piece_type_spaces("rook", color, position_dict=position_dict, all_moves=all_moves) if (rook and (rook != "xx"))]  # Remove empty strings and xxs

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
                if self.get_what_is_on_square_specific(square, position_dict=position_dict) != "None":
                    # print(f"{color} can't castle kingside, something is blocking")
                    break  # Exit the loop immediately if a square is not "None"
            else: legal_castle_moves.append(kingside_castle)

        if castle_queenside: 
            for square in queenside_squares:
                if self.get_what_is_on_square_specific(square, position_dict=position_dict) != "None":
                    # print(f"{color} can't castle queenside, something is blocking")
                    break  # Exit the loop immediately if a square is not "None"
            else: legal_castle_moves.append(queenside_castle)

        # print (legal_castle_moves)
        return legal_castle_moves

        
            #Pawns moving 1 and 2 spaces forward
    
    def get_legal_pawn_normal_moves(self, color, position_dict, all_moves): 
        legal_pawn_normal_moves = []
        pawn_positions = [pawn for pawn in self.piece_type_spaces("pawn", color, position_dict=position_dict, all_moves=all_moves) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
        # pawn_positions = [pawn for pawn in piece_type_spaces("pawn", color) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
        direction = [1,2] if color.lower() == "white" else [-1,-2]
        for pawn in pawn_positions:
            for offset in direction:
                if offset in [2, -2] and pawn[1] != ("2" if color.lower() == "white" else "7"): continue
                new_rank = int(pawn[1]) + offset
                # if 1 <= new_rank <= 8:
                if (color.lower() == "white" and 1 <= new_rank <= 7) or (color.lower() == "black" and 2 <= new_rank <= 8):
                    potential_position = f"{pawn[0]}{new_rank}"
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)
                    if piece == "None" and color.lower() not in piece.lower():
                        legal_pawn_normal_moves.append(f"{pawn}{potential_position}")
                    else: break

        return legal_pawn_normal_moves

    def get_legal_en_passant_moves(self, color, position_dict, all_moves):  
        legal_en_passant_moves = []
        if not all_moves:
            return
        last_move = all_moves[-1]
        pawn_positions = [pawn for pawn in self.piece_type_spaces("pawn", color, position_dict=position_dict, all_moves=all_moves) if (pawn and (pawn != "xx"))]  # Remove empty strings and xxs
        en_passant_data = {
            "white": ("5", [(-1,1), (1, 1)]),
            "black": ("4", [(-1,-1), (1, -1)]),
        }

        rank, direction = en_passant_data[color.lower()]
        for pawn in pawn_positions:
            same_rank = pawn[1] == rank
            last_move_same_rank = last_move[3] == rank
            adjacent_file = last_move[2] in (chr(ord(pawn[0]) + 1), chr(ord(pawn[0]) - 1))
            #ex: b7b5
            moved_two_squares = abs(int(last_move[1]) - int(last_move[3])) == 2
            # input(f"{int(last_move[1])} - {int(last_move[3])}")
            if same_rank and last_move_same_rank and adjacent_file and moved_two_squares:
                from_square = pawn
                for sub_direction in direction:
                    new_file = chr(ord(pawn[0]) + sub_direction[0])
                    new_rank = int(pawn[1]) + sub_direction[1]

                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        if new_file == last_move[2]:
                            to_square = f"{new_file}{new_rank}"
                            legal_en_passant_moves.append(from_square + to_square)

        # print(legal_en_passant_moves)
        return legal_en_passant_moves

    def get_legal_bishop_moves(self, color, position_dict, all_moves): 
        opposite_color = "black" if color.lower() == "white" else "white"
        legal_bishop_capture_moves = []
        bishop_positions = [bishop for bishop in self.piece_type_spaces("bishop", color, position_dict=position_dict, all_moves=all_moves) if (bishop and (bishop != "xx") and not bishop[-1].isalpha())]  # Remove empty strings and xxs
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
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)

                    if piece == "None" and not enemy_encountered:
                        legal_bishop_capture_moves.append(f"{bishop}{potential_position}")

                    elif opposite_color.lower() in piece.lower() and not enemy_encountered: 
                        legal_bishop_capture_moves.append(f"{bishop}{potential_position}")
                        enemy_encountered = True
                        
                    else:
                        break  # Stop if blocked by own piece or after capturing an enemy

        return legal_bishop_capture_moves

    def get_legal_rook_moves(self, color, position_dict, all_moves): 
        opposite_color = "black" if color.lower() == "white" else "white"
        legal_rook_capture_moves = []
        rook_positions = [rook for rook in self.piece_type_spaces("rook", color, position_dict=position_dict, all_moves=all_moves) if (rook and (rook != "xx") and not rook[-1].isalpha())]  # Remove empty strings and xxs
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
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)

                    if piece == "None" and not enemy_encountered:
                        legal_rook_capture_moves.append(f"{rook}{potential_position}")

                    elif opposite_color.lower() in piece.lower() and not enemy_encountered: 
                        legal_rook_capture_moves.append(f"{rook}{potential_position}")
                        enemy_encountered = True
                        
                    else:
                        break  # Stop if blocked by own piece or after capturing an enemy

        return legal_rook_capture_moves

    def get_legal_queen_moves(self, color, position_dict, all_moves): 
        opposite_color = "black" if color.lower() == "white" else "white"
        legal_queen_capture_moves = []
        queen_positions = [queen for queen in self.piece_type_spaces("queen", color, position_dict=position_dict, all_moves=all_moves) if (queen and (queen != "xx") and not queen[-1].isalpha())]  # Remove empty strings and xxs
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
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)
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

    def get_legal_king_moves(self, color, position_dict, all_moves):
        opposite_color = "black" if color.lower() == "white" else "white"
        legal_king_moves = []
        king_positions = [king for king in self.piece_type_spaces("king", color, position_dict=position_dict, all_moves=all_moves) if (king and (king != "xx") and not king[-1].isalpha())]  # Remove empty strings and xxs
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]  # (delta_file, delta_rank) for up, down, right, left, and diagonals
        for king in king_positions:
            for delta_file, delta_rank in directions:
                file, rank = king[0], int(king[1])
                file = chr(ord(file) + delta_file)
                rank += delta_rank
                potential_position = f"{file}{rank}"
                if 'a' <= file <= 'h' and 1 <= rank <= 8:
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)
                    if color.lower() not in piece.lower():
                        legal_king_moves.append(f"{king}{potential_position}")

        # print(f"{color} legal_king_moves: {legal_king_moves}")
        return legal_king_moves

    def get_legal_promoted_pawn_moves(self, color, position_dict, all_moves):
        opposite_color = "black" if color.lower() == "white" else "white"
        #not doing enpassant, because this is for scanning for checks
        legal_pawn_promotion_moves = []
        pawn_positions = [pawn for pawn in self.piece_type_spaces("pawn", color, position_dict=position_dict, all_moves=all_moves) if pawn and pawn != "xx" and not pawn[-1].isalpha()]
        direction = 1 if color.lower() == "white" else -1
        for pawn in pawn_positions:
            for offset in [-1, 1, 0]:  # Check left (-1) and right (+1) diagonals
                new_file = chr(ord(pawn[0]) + offset)
                new_rank = int(pawn[1]) + direction
                # print(f"pawn: {pawn}, new_file: {new_file}, new_rank: {new_rank}")
                if "a" <= new_file <= "h" and ((color.lower() == "white" and new_rank == 8) or (color.lower() == "black" and new_rank == 1)):
                    potential_position = f"{new_file}{new_rank}"
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)

                    #moving straight forward allowed
                    if offset == 0 and piece == "None":
                        for abbreviation in self.abbreviation_dict.items():
                            if abbreviation != "k" and abbreviation != "p":
                                legal_pawn_promotion_moves.append(f"{pawn}{potential_position}{abbreviation[0]}")

                    #moving diagonal allowed
                    if offset != 0 and piece != "None":
                        for abbreviation in self.abbreviation_dict.items():
                            if abbreviation != "k" and abbreviation != "p":
                                legal_pawn_promotion_moves.append(f"{pawn}{potential_position}{abbreviation[0]}")
        # print(legal_pawn_promotion_moves)
        return legal_pawn_promotion_moves

    def get_legal_knight_moves(self, color, position_dict, all_moves):
        opposite_color = "black" if color.lower() == "white" else "white"
        legal_knight_moves = []
        knight_positions = [knight for knight in self.piece_type_spaces("knight", color, position_dict=position_dict, all_moves=all_moves) if (knight and (knight != "xx") and not knight[-1].isalpha())]  # Remove empty strings and xxs
        directions = [(1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, 1), (2, -1)]  # (delta_file, delta_rank) for 8 knight positions
        for knight in knight_positions:
            for delta_file, delta_rank in directions:
                file, rank = knight[0], int(knight[1])
                file = chr(ord(file) + delta_file)
                rank += delta_rank
                potential_position = f"{file}{rank}"
                if 'a' <= file <= 'h' and 1 <= rank <= 8:
                    piece = self.get_what_is_on_square_specific(potential_position, position_dict=position_dict)
                    if color.lower() not in piece.lower():
                        legal_knight_moves.append(f"{knight}{potential_position}")
        return legal_knight_moves  

    def get_what_is_on_square_specific(self, square, position_dict):
        if not isinstance(position_dict, dict):
            raise TypeError(f"Expected a dictionary, got {type(position_dict)}")

        for key, val in position_dict.items():
            if isinstance(val, str) and val == square:
                return key
        return "None"
    
    def is_en_passant_move(self, given_move, turn_color, position_dict, all_moves, loading=False, loaded_last_move=""):
        color = turn_color
        opposite_color = "black" if color.lower() == "white" else "white"
        potential_position = given_move[2:4]
        if not all_moves or len(given_move) != 4: return False
        last_move = all_moves[-1] if not loading else loaded_last_move
        en_passant_data = {
            "white": ("5", -1),
            "black": ("4", 1),
        }
        rank, direction = en_passant_data[color.lower()]
        moving_piece = self.get_what_is_on_square_specific(given_move[:2], position_dict=position_dict)
        removed_piece_position = potential_position[0] + chr(ord(potential_position[1]) + direction)
        removed_piece = self.get_what_is_on_square_specific(removed_piece_position, position_dict=position_dict).lower()

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
    
    def do_temp_capture(self, removed_piece, position_dict, all_moves):
        position_dict[removed_piece] = "xx"

    def undo_temp_capture(self, removed_piece, square, en_passant_removed_square,position_dict, all_moves):
        if en_passant_removed_square: 
            position_dict[removed_piece] = en_passant_removed_square
            return
        position_dict[removed_piece] = square

    #used to find the positions of a desired piece type
    #example: returns all the positions of the black pawns
    def piece_type_spaces(self, wanted_piece, color, position_dict, all_moves):
        piece_positions = []
        # if position_dict is None: raise ValueError("position_dict is None in piece_type_spaces")
        for piece in position_dict:
            if ((wanted_piece.lower() in piece.lower()) and (color.lower() in piece.lower())):
                piece_positions.append(position_dict[piece])
        return piece_positions

    #implement the command with the capture, and updating the piece positions before printing them again
    def implement_command(self, command, piece, position_dict, all_moves, board_positions_list, update=True, loaded_last_move=""):
        if update: position_dict = self.handle_capture(command, position_dict=position_dict, all_moves=all_moves)
        else: position_dict = self.handle_capture(command, loading=True, loaded_last_move=loaded_last_move, position_dict=position_dict, all_moves=all_moves)

        if len(command) == 5: #if it is a pawn promotion
            position_dict = self.update_promoted_pawn_position(command, piece, position_dict=position_dict, all_moves=all_moves)
        else: 
            position_dict = self.update_piece_position(command[:2], command[-2:], piece, position_dict=position_dict, all_moves=all_moves) #piece is actually a command for castling. fix lingo later
        if update: all_moves = self.update_position(command, all_moves) #Update all moves
        # toggle_turn_color()
        turn_color = self.phoenix_get_turn_from_moves(all_moves)
        opponent_color = "black" if turn_color == "white" else "white"
        board_positions_list.append(
            self.get_possible_moves(turn=turn_color, position_dict=position_dict, all_moves=all_moves) +
            self.get_possible_moves(turn=opponent_color, position_dict=position_dict, all_moves=all_moves) +
            [self.phoenix_get_turn_from_moves(all_moves)]
        )
        return position_dict, all_moves, turn_color, board_positions_list

    #updates all moves with the current moves that have been made
    #only called if not loading a game in implement_command 
    def update_position(self, current_move, all_moves):
        all_moves.append(current_move)
        return all_moves

    #update the position of a piece. The third parameter, command, is a bit confusing right now. it is only used for castling. also reffered to as piece in main
    def update_piece_position(self, initial_position, new_position, command, position_dict, all_moves):
        turn = self.phoenix_get_turn_from_moves(all_moves)
        rook_moves = {
            ("white", "Castle Kingside"): "h1f1",
            ("black", "Castle Kingside"): "h8f8",
            ("white", "Castle Queenside"): "a1d1",
            ("black", "Castle Queenside"): "a8d8",
        }

        for key, val in position_dict.items():
            if val == initial_position:
                position_dict[key] = new_position
                # print(f"{key} is now on {new_position}")

        if (turn, command) in rook_moves:
            # print(f"about to update a rook in a castle command")
            position_dict = self.update_piece_position(rook_moves[turn, command][:2], rook_moves[turn, command][-2:], "Rook move", position_dict=position_dict, all_moves=all_moves) #move the rook
        
        return position_dict

    def update_promoted_pawn_position(self, current_move, piece, position_dict, all_moves): 
        promoted_pawn = self.get_promoted_pawn(current_move, position_dict=position_dict, all_moves=all_moves)
        position_dict[self.get_promoted_pawn(current_move, position_dict=position_dict, all_moves=all_moves)] = current_move[2:4]
        self.change_promoted_pawn(promoted_pawn, current_move, position_dict=position_dict, all_moves=all_moves)
        self.update_piece_position(current_move[:2], "xx", piece, position_dict=position_dict, all_moves=all_moves)
        return position_dict

    def change_promoted_pawn(self, promoted_pawn, current_move, position_dict, all_moves):
        position_dict[self.replace_text(promoted_pawn, "PAWN", self.abbreviation_dict[current_move[-1]].upper())] = position_dict.pop(promoted_pawn)

    #get the name of the promoted pawn, given the regular pawn to be promoted 
    def get_promoted_pawn(self, current_move, position_dict, all_moves):
        return "piece.PROMOTED_" + self.phoenix_get_turn_from_moves(all_moves).upper() + "_PAWN" + self.get_what_is_on_square_specific(current_move[:2], position_dict=position_dict)[-1]

    def rank_capture(self, move, rank_postion_dict, rank_all_moves):
        #if it is a castle, it is still valuable but there is not capture
        if move in ["e1g1", "e8g8", "e1c1", "e8c8"]: return 0
        self.is_en_passant_move
        # self.phoenix_get_turn_from_moves(all_moves)
        if self.is_en_passant_move(move, turn_color=self.phoenix_get_turn_from_moves(rank_all_moves), position_dict=rank_postion_dict, all_moves=rank_all_moves):
            return 100
        else:
            captured_potential = self.get_what_is_on_square_specific(move[-2:], position_dict=rank_postion_dict).lower()
            if captured_potential == "none": return 0
            else: 
                for piece, values in PST_dict.items():
                    if piece in captured_potential:
                        # input(captured_potential)
                        if "white" in captured_potential: 
                            # input("white")
                            return -values[0]
                        else: return values[0]
        
    #the position of pieces that are captured are "xx"
    #works with normal captures and en passants
    def handle_capture(self, move, position_dict, all_moves, loading=False, loaded_last_move=""):
        if self.is_en_passant_move(given_move=move, turn_color=self.phoenix_get_turn_from_moves(all_moves), position_dict=position_dict, all_moves=all_moves, loading=loading, loaded_last_move=loaded_last_move): 

            if self.phoenix_get_turn_from_moves(all_moves) == "white": position_dict = self.record_captured_info(self.get_what_is_on_square_specific(self.decrement_string(move[-2:]), position_dict=position_dict), self.decrement_string(move[-2:]), move, position_dict=position_dict)
            else: position_dict = self.record_captured_info(self.get_what_is_on_square_specific(self.increment_string(move[-2:]), position_dict=position_dict), self.increment_string(move[-2:]), move, position_dict=position_dict)

            self.update_piece_position((self.decrement_string if self.phoenix_get_turn_from_moves(all_moves) == "white" else self.increment_string)(move[-2:]), "xx", "capture", position_dict=position_dict, all_moves=all_moves)
        else: 
            # for key, val in position_dict.items():
                if len(move) == 5: 
                    # if move[2:4] == val: 
                    if self. get_what_is_on_square_specific(move[2:4], position_dict=position_dict) != "None":
                        position_dict = self.record_captured_info(self.get_what_is_on_square_specific(move[2:4], position_dict=position_dict), move[2:4], move, position_dict=position_dict)
                        position_dict = self.update_piece_position(move[2:4], "xx", "capture", position_dict=position_dict, all_moves=all_moves)
                else:
                    # if move[-2:] == val: 
                    if self. get_what_is_on_square_specific(move[-2:], position_dict=position_dict) != "None":
                        position_dict = self.record_captured_info(self.get_what_is_on_square_specific(move[-2:], position_dict=position_dict), move[-2:], move, position_dict=position_dict)
                        position_dict = self.update_piece_position(move[-2:], "xx", "capture", position_dict=position_dict, all_moves=all_moves)
        return position_dict
        
    def record_captured_info(self, captured_piece, captured_position, captured_move, position_dict): 
        position_dict[captured_move] = (captured_piece, captured_position)
        return position_dict

    #used to replace text in a string. Currently used for converting promoted pawns to their new piece type
    def replace_text(self, text, word, replace):
        new_text = text.replace(word, replace)
        return new_text

    # It is white's turn if there have been no moves or an even number of moves,
    # otherwise it's black's turn.
    def phoenix_get_turn_from_moves(self, moves):
        return "black" if len(moves) % 2 == 1 else "white"

    #used by handle_capture for en passant pawn capture positions
    def increment_string(self, s):
        return re.sub(r'(\d+)$', lambda x: str(int(x.group(1)) + 1), s)

    #used by handle_capture for en passant pawn capture positions
    def decrement_string(self, s):
        return re.sub(r'(\d+)$', lambda x: str(int(x.group(1)) - 1), s)

    def evaluate_postion(self, passed_position_dict, no_moves=False, passed_all_moves = [], is_end_game = False):
        # input("inside eval pos")
        if no_moves:
            turn = self.phoenix_get_turn_from_moves(passed_all_moves)
            # print(f"position_dict before: {passed_position_dict}")
            if self.is_king_in_check(turn, position_dict=passed_position_dict, all_moves=passed_all_moves):
                if turn == "white": return -100000
                else: return 100000
            else: return 0
        
        # input(f"position_dict after: {passed_position_dict}")

        if self.check_for_insufficient_material_draw(passed_position_dict): return 0

        position_eval = 0
        # print(passed_position_dict)
        for piece, position in passed_position_dict.items():
            if position == "xx": continue
            if not isinstance(position, str): continue
            piece_type = next((p for p in ("king", "queen", "rook", "bishop", "knight", "pawn") if p in piece.lower()), None)
            if piece_type == None: 
                print(f"586 error: passed_postion_dict: {passed_position_dict}, piece, position: {piece, position}, passed_all_moves: {passed_all_moves}")
                exit()
            #evaluate with respect to white
            if piece_type == "king": 
                piece_type = "king_end" if is_end_game else "king_middle"
            if "white" in piece.lower():
                # input(f"white {piece}, {piece_type}, {position}")
                position_eval += (PST_dict[piece_type][0] + PST_dict[piece_type][1][self.square_to_index(position)])
            
            #evaluate with respect to black                
            else:
                # input(f"black {piece}, {piece_type}, {position}")
                position_eval -= (PST_dict[piece_type][0] + PST_dict[piece_type][1][self.square_to_index((PST_reversed[position]))])
        return position_eval

    def evaluate_piece_test(self, piece, position):
        if any(p in piece for p in ("king", "queen", "rook", "bishop", "knight", "pawn")):
            # print(piece)
            # print(PST_dict[piece])
            # print(PST_dict[piece][0])
            # print(self.square_to_index(position))

            # for i in range(0, 64):
            #     print(f"Space {i}: ")
            # #     print(white_queen_PST[i])

            # print(white_queen_PST[63])

            # print(PST_dict[piece][1][self.square_to_index(position)])
            # print(PST_dict[piece][0] + PST_dict[piece][1][self.square_to_index(position)])
            return (PST_dict[piece][0] + PST_dict[piece][1][self.square_to_index(position)])

    def check_for_insufficient_material_draw(self, passed_position_dict):
        black_bishop_count_total = 0
        black_dark_bishop_count = 0
        black_light_bishop_count = 0

        white_bishop_count_total = 0
        white_dark_bishop_count = 0
        white_light_bishop_count = 0

        black_knight_count = 0
        white_knight_count = 0

        for piece, position in passed_position_dict.items():
            #any position that has a queen is not insufficient material
            if "queen" in piece.lower() and position and position != "xx": return False
            #same with rook
            if "rook" in piece.lower() and position and position != "xx": return False
            #same with pawn (can be promoted)
            if "pawn" in piece.lower() and position and position != "xx": return False
            #black bishop count
            if "bishop" in piece.lower() and "black" in piece.lower() and position and position != "xx": 
                black_bishop_count_total += 1
                if self.is_dark_square(position): black_dark_bishop_count += 1
                else: black_light_bishop_count += 1
            #white bishop count
            if "bishop" in piece.lower() and "white" in piece.lower() and position and position != "xx": 
                white_bishop_count_total += 1
                if self.is_dark_square(position): white_dark_bishop_count += 1
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
    def is_dark_square(self, square):
        file = square[0].lower()  # e.g., 'e'
        rank = int(square[1])     # e.g., 4

        # Convert file letter to a number (a=1, b=2, ..., h=8)
        file_index = ord(file) - ord('a') + 1

        # Dark if sum is even, light if odd
        return (file_index + rank) % 2 == 0

    def square_to_index(self, square):
        # print(square)
        file = square[0]
        rank = square[1]
        # print(f"file: {file}, rank: {rank}")
        file_number = ord(file) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
        rank_number = int(rank)             # '1' -> 1, '8' -> 8

        return (rank_number - 1) * 8 + file_number

    def rotate_90_clockwise(self, square_list):
        # Ensure the input list has exactly 64 elements
        if len(square_list) != 64:
            raise ValueError("The input must be a list of 64 numbers.")

        # Rotate the square 90 degrees clockwise
        rotated_list = []
        for col in range(8):
            for row in range(7, -1, -1):
                rotated_list.append(square_list[row * 8 + col])
        
        return rotated_list

    def print_as_square(self):
        square_list = self.rotate_90_clockwise(white_king_end_PST)
        # Print the list formatted as an 8x8 square
        for i in range(8):
            print(square_list[i * 8:(i + 1) * 8])

    def is_endgame(self, passed_position_dict):
        total_material = 0
        has_white_queen = False
        has_black_queen = False

        for piece in passed_position_dict:
            if not piece.lower().startswith("piece"): continue
            if "king" in piece.lower():
                continue
            if "queen" in piece.lower():
                if "white" in piece.lower():
                    has_white_queen = True
                else:
                    has_black_queen = True
                total_material += 9
            elif "rook" in piece.lower():
                total_material += 5
            elif "bishop" in piece.lower():
                total_material += 3
            elif "knight" in piece.lower():
                total_material += 3
            elif "pawn" in piece.lower():
                total_material += 1

        if not has_white_queen and not has_black_queen:
            return True
        if (not has_white_queen or not has_black_queen) and total_material <= 13:
            return True

        return False


#region PST_reversed
#for black's perspective
PST_reversed = {
    "a1": "h8", "b1": "g8", "c1": "f8", "d1": "e8", "e1": "d8", "f1": "c8", "g1": "b8", "h1": "a8",
    "a2": "h7", "b2": "g7", "c2": "f7", "d2": "e7", "e2": "d7", "f2": "c7", "g2": "b7", "h2": "a7",
    "a3": "h6", "b3": "g6", "c3": "f6", "d3": "e6", "e3": "d6", "f3": "c6", "g3": "b6", "h3": "a6",
    "a4": "h5", "b4": "g5", "c4": "f5", "d4": "e5", "e4": "d5", "f4": "c5", "g4": "b5", "h4": "a5",
    "a5": "h4", "b5": "g4", "c5": "f4", "d5": "e4", "e5": "d4", "f5": "c4", "g5": "b4", "h5": "a4",
    "a6": "h3", "b6": "g3", "c6": "f3", "d6": "e3", "e6": "d3", "f6": "c3", "g6": "b3", "h6": "a3",
    "a7": "h2", "b7": "g2", "c7": "f2", "d7": "e2", "e7": "d2", "f7": "c2", "g7": "b2", "h7": "a2",
    "a8": "h1", "b8": "g1", "c8": "f1", "d8": "e1", "e8": "d1", "f8": "c1", "g8": "b1", "h8": "a1"
}
#endregion
#region white_pawn_PST
#  0,  0,  0,  0,  0,  0,  0,  0,
# 50, 50, 50, 50, 50, 50, 50, 50,
# 10, 10, 20, 30, 30, 20, 10, 10,
#  5,  5, 10, 25, 25, 10,  5,  5,
#  0,  0,  0, 20, 20,  0,  0,  0,
#  5, -5,-10,  0,  0,-10, -5,  5,
#  5, 10, 10,-20,-20, 10, 10,  5,
#  0,  0,  0,  0,  0,  0,  0,  0
# ^^a1

#ordered: a1, a2, a3, a4, a5, a6, a7, a8
        # ...
        #h1, h2, h3, h4, h5, h6, h7, h8
white_pawn_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10,-20,-20, 10, 10,  5,
    5, -5,-10,  0,  0,-10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]


#endregion
#region white_knight_PST
# -50,-40,-30,-30,-30,-30,-40,-50,
# -40,-20,  0,  0,  0,  0,-20,-40,
# -30,  0, 10, 15, 15, 10,  0,-30,
# -30,  5, 15, 20, 20, 15,  5,-30,
# -30,  0, 15, 20, 20, 15,  0,-30,
# -30,  5, 10, 15, 15, 10,  5,-30,
# -40,-20,  0,  5,  5,  0,-20,-40,
# -50,-40,-30,-30,-30,-30,-40,-50,
# ^^a1

#formatted same as white_pawn_PST
white_knight_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

#endregion
#region white_bishop_PST
# -20,-10,-10,-10,-10,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5, 10, 10,  5,  0,-10,
# -10,  5,  5, 10, 10,  5,  5,-10,
# -10,  0, 10, 10, 10, 10,  0,-10,
# -10, 10, 10, 10, 10, 10, 10,-10,
# -10,  5,  0,  0,  0,  0,  5,-10,
# -20,-10,-10,-10,-10,-10,-10,-20,
# ^^a1
#formatted same as white_pawn_PST
white_bishop_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]
#endregion
#region white_rook_PST
#   0,  0,  0,  0,  0,  0,  0,  0,
#   5, 10, 10, 10, 10, 10, 10,  5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#   0,  0,  0,  5,  5,  0,  0,  0
# ^^a1

#formatted same as white_pawn_PST
white_rook_PST = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]
#endregion
#region white_queen_PST
# -20,-10,-10, -5, -5,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5,  5,  5,  5,  0,-10,
#  -5,  0,  5,  5,  5,  5,  0, -5,
#   0,  0,  5,  5,  5,  5,  0, -5,
# -10,  5,  5,  5,  5,  5,  0,-10,
# -10,  0,  5,  0,  0,  0,  0,-10,
# -20,-10,-10, -5, -5,-10,-10,-20
# ^^a1

#formatted same as white_pawn_PST
white_queen_PST = [

    -20,-10,-10, -5, -5,-10,-10,-20, 
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
    0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

#endregion
#region white_king_middle_PST
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -20,-30,-30,-40,-40,-30,-30,-20,
# -10,-20,-20,-20,-20,-20,-20,-10,
#  20, 20,  0,  0,  0,  0, 20, 20,
#  20, 30, 10,  0,  0, 10, 30, 20
# ^^a1

#formatted same as white_pawn_PST
white_king_middle_PST = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]
#endregion
#region white_king_end_PST
# -50, -40, -30, -20, -20, -30, -40, -50,
# -30, -20, -10, 0, 0, -10, -20, -30,
# -30, -10, 20, 30, 30, 20, -10, -30,
# -30, -10, 30, 40, 40, 30, -10, -30,
# -30, -10, 30, 40, 40, 30, -10, -30,
# -30, -10, 20, 30, 30, 20, -10, -30,
# -30, -30, 0, 0, 0, 0, -30, -30,
# -50, -30, -30, -30, -30, -30, -30, -50
# ^^a1

#formatted same as white_pawn_PST
white_king_end_PST = [
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]

#endregion

PST_dict = {
    "pawn": (100, white_pawn_PST),

    "knight": (300, white_knight_PST),

    "bishop": (300, white_bishop_PST),

    "rook": (500, white_rook_PST),

    "queen": (900, white_queen_PST),

    # "king": (0, white_king_middle_PST)
    "king_middle": (0, white_king_middle_PST),

    "king_end": (0, white_king_end_PST)
}