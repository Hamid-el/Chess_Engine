import numpy as np
from typing import Tuple, List, Optional, Dict

# Piece constants
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

class Board:
    """Chess board representation with piece positions and game state."""
    
    def __init__(self, fen: str = None):
        # Board is represented as 8x8 numpy array
        # 0 = empty, 1-6 = piece type, sign indicates color (+ for white, - for black)
        self.squares = np.zeros((8, 8), dtype=np.int8)
        
        # Game state
        self.side_to_move = WHITE
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant_square = None
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_number = 1
        self.move_history = []
        
        # Initialize the board
        if fen:
            self.load_from_fen(fen)
        else:
            self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the initial position of a chess game."""
        # Set up pawns
        for file in range(8):
            self.squares[1][file] = PAWN  # White pawns
            self.squares[6][file] = -PAWN  # Black pawns
        
        # Set up other pieces
        back_rank = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for file in range(8):
            self.squares[0][file] = back_rank[file]     # White pieces
            self.squares[7][file] = -back_rank[file]    # Black pieces
    
    def load_from_fen(self, fen: str):
        """Load position from FEN notation."""
        parts = fen.split()
        
        # Parse board position
        position = parts[0]
        rank, file = 7, 0
        
        fen_piece_map = {
            'P': PAWN, 'N': KNIGHT, 'B': BISHOP, 'R': ROOK, 'Q': QUEEN, 'K': KING,
            'p': -PAWN, 'n': -KNIGHT, 'b': -BISHOP, 'r': -ROOK, 'q': -QUEEN, 'k': -KING
        }
        
        for char in position:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                self.squares[rank][file] = fen_piece_map[char]
                file += 1
        
        # Parse side to move
        self.side_to_move = WHITE if parts[1] == 'w' else BLACK
        
        # Parse castling rights
        self.castling_rights = {
            'K': 'K' in parts[2],
            'Q': 'Q' in parts[2],
            'k': 'k' in parts[2],
            'q': 'q' in parts[2]
        }
        
        # Parse en passant target square
        self.en_passant_square = None if parts[3] == '-' else self._algebraic_to_coords(parts[3])
        
        # Parse halfmove clock and fullmove number
        if len(parts) > 4:
            self.halfmove_clock = int(parts[4])
        if len(parts) > 5:
            self.fullmove_number = int(parts[5])
    
    def _algebraic_to_coords(self, algebraic: str) -> Tuple[int, int]:
        """Convert algebraic notation (e.g., 'e4') to board coordinates."""
        file = ord(algebraic[0]) - ord('a')
        rank = int(algebraic[1]) - 1
        return rank, file
    
    def _coords_to_algebraic(self, coords: Tuple[int, int]) -> str:
        """Convert board coordinates to algebraic notation."""
        rank, file = coords
        return chr(file + ord('a')) + str(rank + 1)
    
    def get_piece(self, square: Tuple[int, int]) -> int:
        """Get the piece at a given square."""
        rank, file = square
        return self.squares[rank][file]
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        # Implementation will check for checkmate, stalemate, draw by repetition, etc.
        return False
    
    def get_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all legal moves for the current position."""
        # For full implementation, this would use a move generator
        # For now, returning an empty list as a placeholder
        return []
    
    def make_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]]):
        """Make a move on the board."""
        from_square, to_square = move
        from_rank, from_file = from_square
        to_rank, to_file = to_square
        
        # Store the move for history
        self.move_history.append((move, self.squares[to_rank][to_file]))
        
        # Move the piece
        self.squares[to_rank][to_file] = self.squares[from_rank][from_file]
        self.squares[from_rank][from_file] = EMPTY
        
        # Switch sides
        self.side_to_move = 1 - self.side_to_move
        
        # Update fullmove counter
        if self.side_to_move == WHITE:
            self.fullmove_number += 1
    
    def undo_move(self):
        """Undo the last move."""
        if not self.move_history:
            return
        
        (from_square, to_square), captured_piece = self.move_history.pop()
        from_rank, from_file = from_square
        to_rank, to_file = to_square
        
        # Restore the moved piece to its original square
        self.squares[from_rank][from_file] = self.squares[to_rank][to_file]
        self.squares[to_rank][to_file] = captured_piece
        
        # Switch sides back
        self.side_to_move = 1 - self.side_to_move
        
        # Update fullmove counter
        if self.side_to_move == BLACK:
            self.fullmove_number -= 1
    
    def to_fen(self) -> str:
        """Convert the current board position to FEN notation."""
        # Implement FEN generation for the current board state
        return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Default starting position 
        
    def get_copy(self) -> 'Board':
        """Create and return a deep copy of the current board."""
        board_copy = Board()
        
        # Copy the board state
        board_copy.squares = self.squares.copy()
        board_copy.side_to_move = self.side_to_move
        board_copy.castling_rights = self.castling_rights.copy()
        board_copy.en_passant_square = self.en_passant_square
        board_copy.halfmove_clock = self.halfmove_clock
        board_copy.fullmove_number = self.fullmove_number
        
        # Note: We don't copy move_history as it's not needed for display
        
        return board_copy 