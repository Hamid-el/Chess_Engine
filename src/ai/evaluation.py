import numpy as np
from src.core.board import Board, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK

class Evaluator:
    """Evaluates a chess position and returns a numerical score."""
    
    def __init__(self):
        # Material values
        self.piece_values = {
            PAWN: 100,
            KNIGHT: 320,
            BISHOP: 330,
            ROOK: 500,
            QUEEN: 900,
            KING: 20000
        }
        
        # Piece-square tables for positional evaluation
        # These tables encourage pieces to move to good squares
        self.pawn_table = np.array([
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ])
        
        self.knight_table = np.array([
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ])
        
        self.bishop_table = np.array([
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5,  5,  5,  5,  5,-10],
            [-10,  0,  5,  0,  0,  5,  0,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ])
        
        self.rook_table = np.array([
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ])
        
        self.queen_table = np.array([
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ])
        
        self.king_table_middlegame = np.array([
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ])
        
        self.king_table_endgame = np.array([
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-30,-30,-30,-30,-30,-30,-50]
        ])
        
    def evaluate(self, board: Board) -> int:
        """Calculate a numerical score for the position. Positive favors white, negative favors black."""
        if self._is_checkmate(board):
            # Return a large value with sign based on side to move
            return -100000 if board.side_to_move == WHITE else 100000
        
        if self._is_draw(board):
            return 0
        
        score = 0
        
        # Material evaluation
        score += self._evaluate_material(board)
        
        # Piece position evaluation
        score += self._evaluate_piece_positions(board)
        
        # Mobility (simplified)
        score += self._evaluate_mobility(board)
        
        # Adjust for the side to move
        if board.side_to_move == BLACK:
            score = -score
        
        return score
    
    def _evaluate_material(self, board: Board) -> int:
        """Calculate the material balance."""
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board.squares[rank][file]
                if piece != 0:
                    # Add piece value with sign (positive for white, negative for black)
                    piece_type = abs(piece)
                    score += self.piece_values[piece_type] * (1 if piece > 0 else -1)
        
        return score
    
    def _evaluate_piece_positions(self, board: Board) -> int:
        """Evaluate piece positions using piece-square tables."""
        score = 0
        is_endgame = self._is_endgame(board)
        
        for rank in range(8):
            for file in range(8):
                piece = board.squares[rank][file]
                
                if piece == 0:
                    continue
                
                piece_type = abs(piece)
                is_white = piece > 0
                
                # The tables are oriented with white at the bottom (rank 0-1)
                # So for black pieces we need to flip the rank
                pos_rank = rank if is_white else 7 - rank
                
                # Add position score
                if piece_type == PAWN:
                    score += self.pawn_table[pos_rank][file] * (1 if is_white else -1)
                elif piece_type == KNIGHT:
                    score += self.knight_table[pos_rank][file] * (1 if is_white else -1)
                elif piece_type == BISHOP:
                    score += self.bishop_table[pos_rank][file] * (1 if is_white else -1)
                elif piece_type == ROOK:
                    score += self.rook_table[pos_rank][file] * (1 if is_white else -1)
                elif piece_type == QUEEN:
                    score += self.queen_table[pos_rank][file] * (1 if is_white else -1)
                elif piece_type == KING:
                    if is_endgame:
                        score += self.king_table_endgame[pos_rank][file] * (1 if is_white else -1)
                    else:
                        score += self.king_table_middlegame[pos_rank][file] * (1 if is_white else -1)
        
        return score
    
    def _evaluate_mobility(self, board: Board) -> int:
        """Evaluate piece mobility (simplified version)."""
        # This is a placeholder for a more sophisticated mobility evaluation
        # In a full implementation, would count legal moves for each piece
        return 0
    
    def _is_endgame(self, board: Board) -> bool:
        """Determine if the position is in the endgame phase."""
        # Count major pieces
        queens = 0
        major_pieces = 0
        
        for rank in range(8):
            for file in range(8):
                piece = abs(board.squares[rank][file])
                if piece == QUEEN:
                    queens += 1
                if piece in [ROOK, QUEEN]:
                    major_pieces += 1
        
        # Endgame if both sides have no queens or at most one rook
        return queens == 0 or major_pieces <= 2
    
    def _is_checkmate(self, board: Board) -> bool:
        """Check if the position is checkmate."""
        # Simplified version - would need the move generator for a full implementation
        return False
    
    def _is_draw(self, board: Board) -> bool:
        """Check if the position is a draw."""
        # Simplified version
        return False 