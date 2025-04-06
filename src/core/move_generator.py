from typing import List, Tuple
import numpy as np
from src.core.board import Board, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK, EMPTY

class MoveGenerator:
    """Generates legal moves for a chess position."""
    
    def __init__(self, board: Board):
        self.board = board
    
    def get_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate all legal moves for the current position."""
        pseudo_legal_moves = self._generate_pseudo_legal_moves()
        legal_moves = []
        
        # Filter out moves that would leave the king in check
        for move in pseudo_legal_moves:
            # Make the move
            self.board.make_move(move)
            
            # Check if king is in check
            if not self._is_king_in_check(1 - self.board.side_to_move):
                legal_moves.append(move)
            
            # Undo the move
            self.board.undo_move()
        
        return legal_moves
    
    def _generate_pseudo_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate all pseudo-legal moves (not checking for checks)."""
        moves = []
        side = self.board.side_to_move
        
        # Loop through all squares
        for rank in range(8):
            for file in range(8):
                piece = self.board.squares[rank][file]
                
                # Skip empty squares and opponent's pieces
                if piece == EMPTY:
                    continue
                
                # For white pieces (positive values) when white to move, or black pieces when black to move
                if (piece > 0 and side == WHITE) or (piece < 0 and side == BLACK):
                    piece_type = abs(piece)
                    from_square = (rank, file)
                    
                    # Generate moves based on piece type
                    if piece_type == PAWN:
                        moves.extend(self._generate_pawn_moves(from_square))
                    elif piece_type == KNIGHT:
                        moves.extend(self._generate_knight_moves(from_square))
                    elif piece_type == BISHOP:
                        moves.extend(self._generate_bishop_moves(from_square))
                    elif piece_type == ROOK:
                        moves.extend(self._generate_rook_moves(from_square))
                    elif piece_type == QUEEN:
                        moves.extend(self._generate_queen_moves(from_square))
                    elif piece_type == KING:
                        moves.extend(self._generate_king_moves(from_square))
        
        return moves
    
    def _is_king_in_check(self, side: int) -> bool:
        """Check if the king of the given side is in check."""
        # Find the king
        king_value = KING if side == WHITE else -KING
        king_pos = None
        
        for rank in range(8):
            for file in range(8):
                if self.board.squares[rank][file] == king_value:
                    king_pos = (rank, file)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # No king found (shouldn't happen in a legal chess position)
        
        # Check if any opponent piece can capture the king
        for rank in range(8):
            for file in range(8):
                piece = self.board.squares[rank][file]
                
                # Skip empty squares and friendly pieces
                if piece == EMPTY or (piece > 0 and side == WHITE) or (piece < 0 and side == BLACK):
                    continue
                
                from_square = (rank, file)
                piece_type = abs(piece)
                
                # Generate opponent's moves
                opponent_moves = []
                if piece_type == PAWN:
                    opponent_moves = self._generate_pawn_captures(from_square)
                elif piece_type == KNIGHT:
                    opponent_moves = self._generate_knight_moves(from_square)
                elif piece_type == BISHOP:
                    opponent_moves = self._generate_bishop_moves(from_square)
                elif piece_type == ROOK:
                    opponent_moves = self._generate_rook_moves(from_square)
                elif piece_type == QUEEN:
                    opponent_moves = self._generate_queen_moves(from_square)
                elif piece_type == KING:
                    opponent_moves = self._generate_king_moves(from_square)
                
                # Check if any move can capture the king
                for _, to_square in opponent_moves:
                    if to_square == king_pos:
                        return True
        
        return False
    
    def _generate_pawn_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate pawn moves, including captures."""
        rank, file = from_square
        side = self.board.side_to_move
        moves = []
        
        # Direction of pawn movement (white moves up, black moves down)
        direction = 1 if side == WHITE else -1
        
        # Forward move
        to_rank = rank + direction
        if 0 <= to_rank < 8 and self.board.squares[to_rank][file] == EMPTY:
            moves.append((from_square, (to_rank, file)))
            
            # Double move from starting position
            start_rank = 1 if side == WHITE else 6
            if rank == start_rank:
                to_rank = rank + 2 * direction
                if 0 <= to_rank < 8 and self.board.squares[to_rank][file] == EMPTY:
                    moves.append((from_square, (to_rank, file)))
        
        # Captures
        for file_offset in [-1, 1]:
            to_file = file + file_offset
            to_rank = rank + direction
            
            if 0 <= to_rank < 8 and 0 <= to_file < 8:
                to_piece = self.board.squares[to_rank][to_file]
                
                # Regular capture
                if to_piece != EMPTY and ((to_piece < 0 and side == WHITE) or (to_piece > 0 and side == BLACK)):
                    moves.append((from_square, (to_rank, to_file)))
                
                # En passant capture (to be implemented)
        
        return moves
    
    def _generate_pawn_captures(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate potential pawn captures (for check detection)."""
        rank, file = from_square
        piece = self.board.squares[rank][file]
        side = WHITE if piece > 0 else BLACK
        moves = []
        
        # Direction of pawn movement
        direction = 1 if side == WHITE else -1
        
        # Capture diagonally
        for file_offset in [-1, 1]:
            to_file = file + file_offset
            to_rank = rank + direction
            
            if 0 <= to_rank < 8 and 0 <= to_file < 8:
                moves.append((from_square, (to_rank, to_file)))
        
        return moves
    
    def _generate_knight_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate knight moves."""
        rank, file = from_square
        piece = self.board.squares[rank][file]
        side = WHITE if piece > 0 else BLACK
        moves = []
        
        # Knight moves in all 8 L-shapes
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for rank_offset, file_offset in knight_offsets:
            to_rank = rank + rank_offset
            to_file = file + file_offset
            
            if 0 <= to_rank < 8 and 0 <= to_file < 8:
                to_piece = self.board.squares[to_rank][to_file]
                
                # Move to empty square or capture
                if to_piece == EMPTY or (to_piece > 0 and side == BLACK) or (to_piece < 0 and side == WHITE):
                    moves.append((from_square, (to_rank, to_file)))
        
        return moves
    
    def _generate_sliding_moves(self, from_square: Tuple[int, int], directions) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate sliding piece moves (bishop, rook, queen)."""
        rank, file = from_square
        piece = self.board.squares[rank][file]
        side = WHITE if piece > 0 else BLACK
        moves = []
        
        for rank_dir, file_dir in directions:
            for distance in range(1, 8):
                to_rank = rank + rank_dir * distance
                to_file = file + file_dir * distance
                
                # Break if we're off the board
                if to_rank < 0 or to_rank >= 8 or to_file < 0 or to_file >= 8:
                    break
                
                to_piece = self.board.squares[to_rank][to_file]
                
                if to_piece == EMPTY:
                    # Move to empty square
                    moves.append((from_square, (to_rank, to_file)))
                elif (to_piece > 0 and side == BLACK) or (to_piece < 0 and side == WHITE):
                    # Capture opponent's piece
                    moves.append((from_square, (to_rank, to_file)))
                    break
                else:
                    # Blocked by own piece
                    break
        
        return moves
    
    def _generate_bishop_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate bishop moves."""
        # Bishop moves diagonally
        diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._generate_sliding_moves(from_square, diagonal_directions)
    
    def _generate_rook_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate rook moves."""
        # Rook moves horizontally and vertically
        straight_directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        return self._generate_sliding_moves(from_square, straight_directions)
    
    def _generate_queen_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate queen moves."""
        # Queen moves diagonally, horizontally, and vertically
        all_directions = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        return self._generate_sliding_moves(from_square, all_directions)
    
    def _generate_king_moves(self, from_square: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate king moves, including castling."""
        rank, file = from_square
        piece = self.board.squares[rank][file]
        side = WHITE if piece > 0 else BLACK
        moves = []
        
        # Regular king moves in all 8 directions
        king_offsets = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        
        for rank_offset, file_offset in king_offsets:
            to_rank = rank + rank_offset
            to_file = file + file_offset
            
            if 0 <= to_rank < 8 and 0 <= to_file < 8:
                to_piece = self.board.squares[to_rank][to_file]
                
                # Move to empty square or capture
                if to_piece == EMPTY or (to_piece > 0 and side == BLACK) or (to_piece < 0 and side == WHITE):
                    moves.append((from_square, (to_rank, to_file)))
        
        # Castling (to be implemented)
        
        return moves 