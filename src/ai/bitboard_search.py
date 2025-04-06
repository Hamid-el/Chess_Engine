import time
from typing import Tuple, List, Optional
import numpy as np

from src.core.bitboard import (
    BitBoard, WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    north, south, east, west, north_east, north_west, south_east, south_west,
    get_lsb, FILE_A, FILE_H, RANK_2, RANK_7
)

# Pre-computed knight move patterns
KNIGHT_MOVES = {}
for square in range(64):
    rank, file = square // 8, square % 8
    moves = 0
    for r_offset, f_offset in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
        r, f = rank + r_offset, file + f_offset
        if 0 <= r < 8 and 0 <= f < 8:
            moves |= 1 << (r * 8 + f)
    KNIGHT_MOVES[square] = moves

# Pre-computed king move patterns
KING_MOVES = {}
for square in range(64):
    rank, file = square // 8, square % 8
    moves = 0
    for r_offset, f_offset in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
        r, f = rank + r_offset, file + f_offset
        if 0 <= r < 8 and 0 <= f < 8:
            moves |= 1 << (r * 8 + f)
    KING_MOVES[square] = moves

class BitboardMoveGenerator:
    """Generate legal moves for a chess position using bitboards."""
    
    def __init__(self, board: BitBoard):
        self.board = board
    
    def generate_moves(self) -> List[Tuple[int, int]]:
        """Generate all legal moves for the current position."""
        moves = []
        
        # Whose turn is it?
        side_to_move = self.board.side_to_move
        
        # Get all pieces of the side to move
        pieces = self.board.get_all_pieces(side_to_move)
        
        # Get all opponent pieces
        opponent_pieces = self.board.get_all_pieces(1 - side_to_move)
        
        # Get all occupied squares
        occupied = pieces | opponent_pieces
        
        # Get all empty squares
        empty = self.board.get_empty_squares()
        
        # For each piece of the side to move
        bb = pieces
        while bb:
            # Get the square of the piece
            square = get_lsb(bb)
            
            # Clear the bit
            bb &= bb - 1
            
            # Get the piece type
            piece = self.board.get_piece_at(square)
            piece_type = abs(piece)
            
            # Generate moves based on piece type
            if piece_type == PAWN:
                self._generate_pawn_moves(square, moves, empty, opponent_pieces)
            elif piece_type == KNIGHT:
                self._generate_knight_moves(square, moves, pieces)
            elif piece_type == BISHOP:
                self._generate_bishop_moves(square, moves, pieces, occupied)
            elif piece_type == ROOK:
                self._generate_rook_moves(square, moves, pieces, occupied)
            elif piece_type == QUEEN:
                self._generate_queen_moves(square, moves, pieces, occupied)
            elif piece_type == KING:
                self._generate_king_moves(square, moves, pieces)
        
        return moves
    
    def _generate_pawn_moves(self, square: int, moves: List[Tuple[int, int]], empty: int, opponent_pieces: int):
        """Generate legal pawn moves."""
        # Get the pawn's bitboard (1 bit set at the pawn's position)
        pawn_bb = 1 << square
        
        # Direction depends on color
        if self.board.side_to_move == WHITE:
            # Single push
            single_push = north(pawn_bb) & empty
            if single_push:
                moves.append((square, get_lsb(single_push)))
            
            # Double push from 2nd rank
            if pawn_bb & RANK_2:
                double_push = north(single_push) & empty
                if double_push:
                    moves.append((square, get_lsb(double_push)))
            
            # Captures
            capture_east = north_east(pawn_bb) & opponent_pieces
            if capture_east:
                moves.append((square, get_lsb(capture_east)))
            
            capture_west = north_west(pawn_bb) & opponent_pieces
            if capture_west:
                moves.append((square, get_lsb(capture_west)))
            
            # TODO: En passant and promotions
            
        else:  # BLACK
            # Single push
            single_push = south(pawn_bb) & empty
            if single_push:
                moves.append((square, get_lsb(single_push)))
            
            # Double push from 7th rank
            if pawn_bb & RANK_7:
                double_push = south(single_push) & empty
                if double_push:
                    moves.append((square, get_lsb(double_push)))
            
            # Captures
            capture_east = south_east(pawn_bb) & opponent_pieces
            if capture_east:
                moves.append((square, get_lsb(capture_east)))
            
            capture_west = south_west(pawn_bb) & opponent_pieces
            if capture_west:
                moves.append((square, get_lsb(capture_west)))
            
            # TODO: En passant and promotions
    
    def _generate_knight_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int):
        """Generate legal knight moves."""
        # Get pre-computed knight moves for this square
        knight_moves = KNIGHT_MOVES[square]
        
        # Remove moves to squares with friendly pieces
        knight_moves &= ~friendly_pieces
        
        # Add each move to the list
        bb = knight_moves
        while bb:
            to_square = get_lsb(bb)
            bb &= bb - 1
            moves.append((square, to_square))
    
    def _generate_bishop_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int, occupied: int):
        """Generate legal bishop moves."""
        # Generate moves in all four diagonal directions
        for direction in [north_east, north_west, south_east, south_west]:
            self._generate_sliding_moves(square, moves, friendly_pieces, occupied, direction)
    
    def _generate_rook_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int, occupied: int):
        """Generate legal rook moves."""
        # Generate moves in all four orthogonal directions
        for direction in [north, south, east, west]:
            self._generate_sliding_moves(square, moves, friendly_pieces, occupied, direction)
    
    def _generate_queen_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int, occupied: int):
        """Generate legal queen moves."""
        # Generate moves in all eight directions
        for direction in [north, south, east, west, north_east, north_west, south_east, south_west]:
            self._generate_sliding_moves(square, moves, friendly_pieces, occupied, direction)
    
    def _generate_sliding_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int, occupied: int, direction):
        """Generate sliding moves in a given direction."""
        # Get the piece's bitboard (1 bit set at the piece's position)
        piece_bb = 1 << square
        
        # Generate moves in the given direction
        bb = direction(piece_bb)
        while bb:
            to_square = get_lsb(bb)
            
            # Check if square is occupied
            to_bb = 1 << to_square
            if to_bb & occupied:
                # If it's an enemy piece, we can capture it
                if not (to_bb & friendly_pieces):
                    moves.append((square, to_square))
                # Stop sliding in this direction
                break
            
            # Empty square, add the move
            moves.append((square, to_square))
            
            # Continue sliding
            bb = direction(to_bb)
    
    def _generate_king_moves(self, square: int, moves: List[Tuple[int, int]], friendly_pieces: int):
        """Generate legal king moves."""
        # Get pre-computed king moves for this square
        king_moves = KING_MOVES[square]
        
        # Remove moves to squares with friendly pieces
        king_moves &= ~friendly_pieces
        
        # Add each move to the list
        bb = king_moves
        while bb:
            to_square = get_lsb(bb)
            bb &= bb - 1
            moves.append((square, to_square))
        
        # TODO: Castling


class BitboardSearch:
    """Chess AI search algorithm using bitboards for improved performance."""
    
    def __init__(self, board: BitBoard):
        self.board = board
        self.move_generator = BitboardMoveGenerator(board)
        self.nodes_searched = 0
        self.start_time = 0
        self.time_limit = 0
    
    def search(self, depth: int, time_limit: float = 1.0) -> Tuple[int, int]:
        """
        Search for the best move using alpha-beta pruning with bitboards.
        Returns (from_square, to_square).
        """
        self.nodes_searched = 0
        self.start_time = time.time()
        self.time_limit = time_limit
        
        alpha = float('-inf')
        beta = float('inf')
        
        # Get all legal moves
        legal_moves = self.move_generator.generate_moves()
        
        # If no legal moves, return None
        if not legal_moves:
            return None
        
        best_move = None
        best_value = float('-inf')
        
        # Try each move and select the best one
        for move in legal_moves:
            from_square, to_square = move
            
            # Make the move
            original_board_state = self._save_board_state()
            self.board.make_move(from_square, to_square)
            
            # Search the resulting position
            value = -self._alpha_beta(depth - 1, -beta, -alpha, True)
            
            # Undo the move
            self._restore_board_state(original_board_state)
            
            # Update best move if necessary
            if value > best_value:
                best_value = value
                best_move = move
            
            # Update alpha
            alpha = max(alpha, value)
            
            # Check if time limit is exceeded
            if time.time() - self.start_time > self.time_limit:
                break
        
        print(f"Bitboard nodes searched: {self.nodes_searched}")
        return best_move
    
    def _alpha_beta(self, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """
        Alpha-beta pruning search algorithm.
        Returns the evaluation of the position.
        """
        self.nodes_searched += 1
        
        # Check if time limit is exceeded
        if self.nodes_searched % 1000 == 0 and time.time() - self.start_time > self.time_limit:
            return 0
        
        # Reached maximum depth or game is over, evaluate position
        if depth == 0:  # or self.board.is_game_over():
            return self._evaluate()
        
        # Generate moves
        legal_moves = self.move_generator.generate_moves()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                from_square, to_square = move
                
                # Make the move
                original_board_state = self._save_board_state()
                self.board.make_move(from_square, to_square)
                
                # Search the resulting position
                eval = self._alpha_beta(depth - 1, alpha, beta, False)
                
                # Undo the move
                self._restore_board_state(original_board_state)
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                from_square, to_square = move
                
                # Make the move
                original_board_state = self._save_board_state()
                self.board.make_move(from_square, to_square)
                
                # Search the resulting position
                eval = self._alpha_beta(depth - 1, alpha, beta, True)
                
                # Undo the move
                self._restore_board_state(original_board_state)
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def _evaluate(self) -> float:
        """Evaluate the current position."""
        # Material value
        material = 0
        
        # Piece values (same as in evaluation.py)
        piece_values = {
            PAWN: 100,
            KNIGHT: 320,
            BISHOP: 330,
            ROOK: 500,
            QUEEN: 900,
            KING: 20000
        }
        
        # Calculate material balance
        for piece_type in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]:
            white_count = bin(self.board.bitboards[piece_type]).count('1')
            black_count = bin(self.board.bitboards[-piece_type]).count('1')
            material += (white_count - black_count) * piece_values[piece_type]
        
        # Mobility (simple version)
        mobility = 0
        
        # If it's white's turn, positive score is good for white
        # If it's black's turn, positive score is good for black
        if self.board.side_to_move == BLACK:
            material = -material
        
        return material + mobility
    
    def _save_board_state(self):
        """Save the current board state for later restoration."""
        # Deep copy of the bitboards
        bitboards_copy = {}
        for piece, bb in self.board.bitboards.items():
            bitboards_copy[piece] = bb
        
        return {
            'bitboards': bitboards_copy,
            'side_to_move': self.board.side_to_move,
            'castling_rights': self.board.castling_rights.copy(),
            'en_passant_square': self.board.en_passant_square,
            'halfmove_clock': self.board.halfmove_clock,
            'fullmove_number': self.board.fullmove_number
        }
    
    def _restore_board_state(self, state):
        """Restore a previously saved board state."""
        self.board.bitboards = state['bitboards']
        self.board.side_to_move = state['side_to_move']
        self.board.castling_rights = state['castling_rights']
        self.board.en_passant_square = state['en_passant_square']
        self.board.halfmove_clock = state['halfmove_clock']
        self.board.fullmove_number = state['fullmove_number'] 