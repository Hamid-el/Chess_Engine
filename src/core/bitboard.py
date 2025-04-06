import numpy as np
from typing import List, Tuple, Dict, Optional

# Constants for files and ranks
FILE_A = 0x8080808080808080
FILE_B = 0x4040404040404040
FILE_C = 0x2020202020202020
FILE_D = 0x1010101010101010
FILE_E = 0x0808080808080808
FILE_F = 0x0404040404040404
FILE_G = 0x0202020202020202
FILE_H = 0x0101010101010101

RANK_1 = 0x00000000000000FF
RANK_2 = 0x000000000000FF00
RANK_3 = 0x0000000000FF0000
RANK_4 = 0x00000000FF000000
RANK_5 = 0x000000FF00000000
RANK_6 = 0x0000FF0000000000
RANK_7 = 0x00FF000000000000
RANK_8 = 0xFF00000000000000

FILES = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H]
RANKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8]

# Piece constants (match the ones in board.py)
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

# Color constants
WHITE = 0
BLACK = 1

class BitBoard:
    """Represents a chess board using bitboards for efficient operations."""
    
    def __init__(self):
        # Initialize bitboards for each piece type and color
        self.bitboards = {
            # White pieces (positive values)
            PAWN: 0,
            KNIGHT: 0,
            BISHOP: 0,
            ROOK: 0,
            QUEEN: 0,
            KING: 0,
            # Black pieces (negative values)
            -PAWN: 0,
            -KNIGHT: 0,
            -BISHOP: 0,
            -ROOK: 0,
            -QUEEN: 0,
            -KING: 0
        }
        
        # Game state
        self.side_to_move = WHITE
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
        # Setup initial position
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the initial position of a chess game using bitboards."""
        # White pawns on 2nd rank
        self.bitboards[PAWN] = RANK_2
        
        # White pieces on 1st rank
        self.bitboards[ROOK] = get_bit_at(0, 0) | get_bit_at(7, 0)
        self.bitboards[KNIGHT] = get_bit_at(1, 0) | get_bit_at(6, 0)
        self.bitboards[BISHOP] = get_bit_at(2, 0) | get_bit_at(5, 0)
        self.bitboards[QUEEN] = get_bit_at(3, 0)
        self.bitboards[KING] = get_bit_at(4, 0)
        
        # Black pawns on 7th rank
        self.bitboards[-PAWN] = RANK_7
        
        # Black pieces on 8th rank
        self.bitboards[-ROOK] = get_bit_at(0, 7) | get_bit_at(7, 7)
        self.bitboards[-KNIGHT] = get_bit_at(1, 7) | get_bit_at(6, 7)
        self.bitboards[-BISHOP] = get_bit_at(2, 7) | get_bit_at(5, 7)
        self.bitboards[-QUEEN] = get_bit_at(3, 7)
        self.bitboards[-KING] = get_bit_at(4, 7)
    
    def get_all_pieces(self, color: int) -> int:
        """Get bitboard with all pieces of given color."""
        if color == WHITE:
            return (self.bitboards[PAWN] | self.bitboards[KNIGHT] | self.bitboards[BISHOP] | 
                    self.bitboards[ROOK] | self.bitboards[QUEEN] | self.bitboards[KING])
        else:
            return (self.bitboards[-PAWN] | self.bitboards[-KNIGHT] | self.bitboards[-BISHOP] | 
                    self.bitboards[-ROOK] | self.bitboards[-QUEEN] | self.bitboards[-KING])
    
    def get_all_pieces_both_colors(self) -> int:
        """Get bitboard with all pieces on the board."""
        return self.get_all_pieces(WHITE) | self.get_all_pieces(BLACK)
    
    def get_empty_squares(self) -> int:
        """Get bitboard with all empty squares."""
        return ~self.get_all_pieces_both_colors() & 0xFFFFFFFFFFFFFFFF
    
    def get_piece_at(self, square: int) -> int:
        """Get piece at the given square (0-63)."""
        square_bit = 1 << square
        
        for piece in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]:
            if self.bitboards[piece] & square_bit:
                return piece
            if self.bitboards[-piece] & square_bit:
                return -piece
        
        return EMPTY

    def make_move(self, from_square: int, to_square: int):
        """Make a move on the bitboard."""
        # Get the piece that's moving
        piece = self.get_piece_at(from_square)
        if piece == EMPTY:
            return False
        
        # Check if it's the right color to move
        if (piece > 0 and self.side_to_move != WHITE) or (piece < 0 and self.side_to_move != BLACK):
            return False
        
        # Create bit masks for from and to squares
        from_bit = 1 << from_square
        to_bit = 1 << to_square
        
        # Remove any captured piece from its bitboard
        captured = self.get_piece_at(to_square)
        if captured != EMPTY:
            self.bitboards[captured] &= ~to_bit
        
        # Move the piece (clear from square, set to square)
        self.bitboards[piece] &= ~from_bit
        self.bitboards[piece] |= to_bit
        
        # Update game state
        self.side_to_move = 1 - self.side_to_move
        if self.side_to_move == WHITE:
            self.fullmove_number += 1
        
        return True
    
    def to_array(self) -> np.ndarray:
        """Convert bitboard to 8x8 numpy array representation."""
        board_array = np.zeros((8, 8), dtype=np.int8)
        
        for piece in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]:
            # White pieces
            bb = self.bitboards[piece]
            while bb:
                # Get least significant bit
                square = get_lsb(bb)
                # Clear the bit
                bb &= bb - 1
                # Convert square to rank and file
                rank = square // 8
                file = square % 8
                # Set the piece in the array
                board_array[rank][file] = piece
            
            # Black pieces
            bb = self.bitboards[-piece]
            while bb:
                square = get_lsb(bb)
                bb &= bb - 1
                rank = square // 8
                file = square % 8
                board_array[rank][file] = -piece
        
        return board_array

    @staticmethod
    def from_array(board_array: np.ndarray):
        """Create a BitBoard from an 8x8 numpy array representation."""
        bitboard = BitBoard()
        
        # Clear all piece bitboards
        for piece in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]:
            bitboard.bitboards[piece] = 0
            bitboard.bitboards[-piece] = 0
        
        # Set pieces from the array
        for rank in range(8):
            for file in range(8):
                piece = board_array[rank][file]
                if piece != EMPTY:
                    square = rank * 8 + file
                    bitboard.bitboards[piece] |= (1 << square)
        
        return bitboard

# Utility functions for bitboard operations
def get_bit_at(file: int, rank: int) -> int:
    """Get bit at the specified file (0-7) and rank (0-7)."""
    square = rank * 8 + file
    return 1 << square

def get_lsb(bitboard: int) -> int:
    """Get the position of the least significant bit (0-63)."""
    if bitboard == 0:
        return -1
    # Python equivalent of __builtin_ctzll
    return (bitboard & -bitboard).bit_length() - 1

def north(bitboard: int) -> int:
    """Shift bitboard north (up) one rank."""
    return (bitboard << 8) & 0xFFFFFFFFFFFFFFFF

def south(bitboard: int) -> int:
    """Shift bitboard south (down) one rank."""
    return bitboard >> 8

def east(bitboard: int) -> int:
    """Shift bitboard east (right) one file."""
    return ((bitboard << 1) & ~FILE_A) & 0xFFFFFFFFFFFFFFFF

def west(bitboard: int) -> int:
    """Shift bitboard west (left) one file."""
    return (bitboard >> 1) & ~FILE_H

def north_east(bitboard: int) -> int:
    """Shift bitboard north-east (up-right) one square."""
    return ((bitboard << 9) & ~FILE_A) & 0xFFFFFFFFFFFFFFFF

def north_west(bitboard: int) -> int:
    """Shift bitboard north-west (up-left) one square."""
    return ((bitboard << 7) & ~FILE_H) & 0xFFFFFFFFFFFFFFFF

def south_east(bitboard: int) -> int:
    """Shift bitboard south-east (down-right) one square."""
    return ((bitboard >> 7) & ~FILE_A) & 0xFFFFFFFFFFFFFFFF

def south_west(bitboard: int) -> int:
    """Shift bitboard south-west (down-left) one square."""
    return ((bitboard >> 9) & ~FILE_H) & 0xFFFFFFFFFFFFFFFF 