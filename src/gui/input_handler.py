import pygame
from typing import Tuple, Optional, Callable
from src.core.game import ChessGame
from src.gui.renderer import BoardRenderer

class InputHandler:
    """Handles user input for the chess game."""
    
    def __init__(self, game: ChessGame, renderer: BoardRenderer):
        self.game = game
        self.renderer = renderer
        self.selected_square = None
        self.drag_start = None
        self.drag_piece = None
        self.dragging = False
        
        # Callback for when the player makes a move
        self.on_move_made: Optional[Callable] = None
    
    def handle_event(self, event) -> bool:
        """
        Handle pygame events.
        Returns True if the event was handled, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                return self._handle_mouse_down(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                return self._handle_mouse_up(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                return self._handle_mouse_motion(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            return self._handle_key_down(event.key)
        
        return False
    
    def _handle_mouse_down(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse button down event."""
        square = self.renderer.screen_to_board_position(pos)
        
        if square is None:
            # Click outside the board
            return False
        
        # Get the piece at the square
        rank, file = square
        piece = self.game.board.get_piece(square)
        
        # Check if clicking on a piece of the current side to move
        is_current_side = (piece > 0 and self.game.board.side_to_move == 0) or \
                          (piece < 0 and self.game.board.side_to_move == 1)
                          
        if piece != 0 and is_current_side:
            # Start dragging the piece
            self.selected_square = square
            self.drag_start = pos
            self.drag_piece = piece
            self.dragging = True
            
            # Update renderer to show selected square and legal moves
            self.renderer.set_selected_square(square)
            
            # Find legal moves for this piece
            legal_moves = []
            for move in self.game.get_legal_moves():
                from_square, _ = move
                if from_square == square:
                    legal_moves.append(move)
            
            self.renderer.set_legal_moves(legal_moves)
            return True
        
        elif self.selected_square is not None:
            # Try to make a move to this square
            if self.game.make_move(self.selected_square, square):
                # Move was made successfully
                self._reset_selection()
                
                # Call the move made callback if set
                if self.on_move_made:
                    self.on_move_made()
            else:
                # Invalid move, reset selection
                self._reset_selection()
            
            return True
        
        return False
    
    def _handle_mouse_up(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse button up event."""
        if not self.dragging:
            return False
        
        square = self.renderer.screen_to_board_position(pos)
        self.dragging = False
        
        if square is None or square == self.selected_square:
            # Dropped outside the board or on the same square
            return True
        
        # Try to make a move
        if self.game.make_move(self.selected_square, square):
            # Move was made successfully
            self._reset_selection()
            
            # Call the move made callback if set
            if self.on_move_made:
                self.on_move_made()
        else:
            # Invalid move, reset selection
            self._reset_selection()
        
        return True
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse motion event while dragging."""
        # This could be used to draw the dragged piece at the cursor position
        # For now, we're just returning True to indicate the event was handled
        return True
    
    def _handle_key_down(self, key: int) -> bool:
        """Handle key down event."""
        if key == pygame.K_ESCAPE:
            # Cancel selection
            if self.selected_square is not None:
                self._reset_selection()
                return True
        
        elif key == pygame.K_u:
            # Undo last move
            if self.game.undo_move():
                self._reset_selection()
                return True
        
        return False
    
    def _reset_selection(self):
        """Reset selection state."""
        self.selected_square = None
        self.drag_start = None
        self.drag_piece = None
        self.dragging = False
        
        # Update renderer
        self.renderer.set_selected_square(None)
        self.renderer.set_legal_moves([])
    
    def set_on_move_made(self, callback: Callable):
        """Set callback for when a move is made."""
        self.on_move_made = callback 