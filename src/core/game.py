from typing import Optional, Tuple, List
from src.core.board import Board
from src.core.move_generator import MoveGenerator

class ChessGame:
    """Main chess game class that manages the game state and rules."""
    
    def __init__(self, fen: str = None):
        self.board = Board(fen)
        self.move_generator = MoveGenerator(self.board)
        self.game_state = "active"  # "active", "checkmate", "stalemate", "draw"
        self.winner = None  # "white", "black", or None (for draw)
        self.move_log = []
        
    def make_move(self, from_square: Tuple[int, int], to_square: Tuple[int, int]) -> bool:
        """
        Attempt to make a move.
        Returns True if move was legal and made, False otherwise.
        """
        move = (from_square, to_square)
        legal_moves = self.move_generator.get_legal_moves()
        
        if move in legal_moves:
            # Store move information for notation and undo
            self.move_log.append({
                "move": move,
                "piece": self.board.get_piece(from_square),
                "captured": self.board.get_piece(to_square),
                "castling_rights": self.board.castling_rights.copy(),
                "en_passant": self.board.en_passant_square,
                "halfmove_clock": self.board.halfmove_clock,
                "fullmove_number": self.board.fullmove_number
            })
            
            # Make the move on the board
            self.board.make_move(move)
            
            # Check for game end conditions
            self._update_game_state()
            
            return True
        
        return False
    
    def undo_move(self) -> bool:
        """Undo the last move if possible."""
        if not self.move_log:
            return False
        
        self.board.undo_move()
        self.move_log.pop()
        self.game_state = "active"
        self.winner = None
        
        return True
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.game_state != "active"
    
    def get_game_result(self) -> Tuple[str, Optional[str]]:
        """Returns tuple of (game_state, winner)."""
        return self.game_state, self.winner
    
    def get_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all legal moves for the current position."""
        return self.move_generator.get_legal_moves()
    
    def _update_game_state(self):
        """Update the game state based on the current board position."""
        legal_moves = self.move_generator.get_legal_moves()
        
        # Check for checkmate or stalemate
        if not legal_moves:
            if self.move_generator._is_king_in_check(self.board.side_to_move):
                self.game_state = "checkmate"
                self.winner = "white" if self.board.side_to_move == 1 else "black"
            else:
                self.game_state = "stalemate"
                self.winner = None
        
        # Check for draw by insufficient material
        elif self._is_insufficient_material():
            self.game_state = "draw"
            self.winner = None
        
        # Check for draw by 50-move rule
        elif self.board.halfmove_clock >= 100:  # 50 moves = 100 ply
            self.game_state = "draw"
            self.winner = None
        
        # Check for draw by threefold repetition (simplified version)
        elif self._is_threefold_repetition():
            self.game_state = "draw"
            self.winner = None
    
    def _is_insufficient_material(self) -> bool:
        """Check if there is insufficient material to deliver checkmate."""
        # Count pieces
        pieces = {
            "wn": 0, "wb": 0, "wr": 0, "wq": 0, "wp": 0,
            "bn": 0, "bb": 0, "br": 0, "bq": 0, "bp": 0
        }
        
        for rank in range(8):
            for file in range(8):
                piece = self.board.get_piece((rank, file))
                if piece == 0:
                    continue
                
                piece_type = abs(piece)
                color = "w" if piece > 0 else "b"
                
                if piece_type == 1:  # Pawn
                    pieces[color + "p"] += 1
                elif piece_type == 2:  # Knight
                    pieces[color + "n"] += 1
                elif piece_type == 3:  # Bishop
                    pieces[color + "b"] += 1
                elif piece_type == 4:  # Rook
                    pieces[color + "r"] += 1
                elif piece_type == 5:  # Queen
                    pieces[color + "q"] += 1
        
        # King vs King
        if sum(pieces.values()) == 0:
            return True
        
        # King and bishop vs King
        if (pieces["wb"] == 1 and sum(pieces.values()) == 1) or (pieces["bb"] == 1 and sum(pieces.values()) == 1):
            return True
        
        # King and knight vs King
        if (pieces["wn"] == 1 and sum(pieces.values()) == 1) or (pieces["bn"] == 1 and sum(pieces.values()) == 1):
            return True
        
        # King and bishop vs King and bishop of same color
        if pieces["wb"] == 1 and pieces["bb"] == 1 and sum(pieces.values()) == 2:
            # Would need to check bishop square colors to be accurate
            return True
        
        return False
    
    def _is_threefold_repetition(self) -> bool:
        """Check for threefold repetition according to FIDE rules.
        
        A position is considered identical if:
        1. The same type of piece is on the same square
        2. The available moves are the same (including castling and en passant)
        3. It's the same player's turn to move
        """
        # We need to track complete positions including castling rights and en passant
        position_history = []
        
        # Add current position
        current_position = self._get_position_key(self.board)
        position_history.append(current_position)
        
        # Check positions from move log
        for i in range(len(self.move_log)):
            # We need to temporarily undo moves to check past positions
            self.board.undo_move()
            position_key = self._get_position_key(self.board)
            position_history.append(position_key)
        
        # Restore the board to current position
        for i in range(len(self.move_log)):
            move_info = self.move_log[i]
            self.board.make_move(move_info["move"])
        
        # Count occurrences of each position
        position_counts = {}
        for pos in position_history:
            position_counts[pos] = position_counts.get(pos, 0) + 1
            if position_counts[pos] >= 3:
                return True
        
        return False
    
    def _get_position_key(self, board):
        """Create a unique key for a board position including castling and en passant."""
        # Get board array representation as a string
        board_str = str(board.squares.tobytes())
        
        # Add side to move
        side_str = "w" if board.side_to_move == 0 else "b"
        
        # Add castling rights
        castling = "".join(k for k, v in board.castling_rights.items() if v)
        if not castling:
            castling = "-"
        
        # Add en passant square
        en_passant = "-" if board.en_passant_square is None else str(board.en_passant_square)
        
        # Combine all elements to create a unique key
        return f"{board_str}_{side_str}_{castling}_{en_passant}" 