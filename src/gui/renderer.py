import pygame
import os
from typing import Tuple, Optional, Dict, List
from src.core.board import Board, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK, EMPTY

class BoardRenderer:
    """Chess board renderer using Pygame."""
    
    def __init__(self, screen: pygame.Surface, board: Board, square_size: int = 80):
        self.screen = screen
        self.board = board
        self.square_size = square_size
        
        # Colors
        self.light_square = (238, 216, 192)  # Light beige
        self.dark_square = (171, 122, 101)   # Dark brown
        self.highlight = (100, 150, 200, 128)  # Semi-transparent blue
        self.move_highlight = (100, 200, 100, 128)  # Semi-transparent green
        self.coordinate_color = (220, 220, 220)  # Lighter color for coordinates
        self.border_color = (80, 70, 60)  # Dark border around the board
        
        # Dimensions
        screen_width, screen_height = screen.get_size()
        self.board_size = 8 * square_size
        
        # Center the board in the available space
        # Leave more room on the right for the UI panel
        right_panel_width = 300  # Estimated width of the right panel
        usable_width = screen_width - right_panel_width
        self.coord_margin = 40  # Space for coordinates
        
        # Center the board in the usable space (left portion of screen)
        self.board_offset_x = (usable_width - self.board_size) // 2
        self.board_offset_y = (screen_height - self.board_size) // 2
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # State
        self.selected_square = None
        self.legal_moves = []
    
    def _load_piece_images(self) -> Dict[int, pygame.Surface]:
        """Load chess piece images from individual PNG files."""
        piece_images = {}
        
        # Path to the pieces directory
        pieces_dir = os.path.join("assets", "graphic", "piece", "pieces-basic-png")
        
        # Mapping of piece type to filename
        piece_filenames = {
            KING: "king",
            QUEEN: "queen", 
            BISHOP: "bishop",
            KNIGHT: "knight",
            ROOK: "rook",
            PAWN: "pawn"
        }
        
        try:
            # Load each piece image individually
            for piece_type, filename in piece_filenames.items():
                # White pieces
                white_path = os.path.join(pieces_dir, f"white-{filename}.png")
                white_img = pygame.image.load(white_path)
                # Use high-quality scaling for pieces - use exact square size for better quality
                white_img = pygame.transform.scale(white_img, (int(self.square_size * 0.9), int(self.square_size * 0.9)))
                piece_images[piece_type] = white_img
                
                # Black pieces
                black_path = os.path.join(pieces_dir, f"black-{filename}.png")
                black_img = pygame.image.load(black_path)
                # Use high-quality scaling for pieces
                black_img = pygame.transform.scale(black_img, (int(self.square_size * 0.9), int(self.square_size * 0.9)))
                piece_images[-piece_type] = black_img
            
            print("Successfully loaded piece images from assets folder")
            
        except Exception as e:
            print(f"Error loading piece images: {e}")
            # Fall back to Unicode symbols with better styling
            piece_symbols = {
                KING: '♔', -KING: '♚',
                QUEEN: '♕', -QUEEN: '♛',
                ROOK: '♖', -ROOK: '♜',
                BISHOP: '♗', -BISHOP: '♝',
                KNIGHT: '♘', -KNIGHT: '♞',
                PAWN: '♙', -PAWN: '♟'
            }
            
            # Create surfaces for each piece with a nice, large font
            font = pygame.font.SysFont('Arial', int(self.square_size * 0.8))
            
            for piece_type, symbol in piece_symbols.items():
                color = (240, 240, 240) if piece_type > 0 else (30, 30, 30)  # White or black pieces
                piece_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                piece_surface.fill((0, 0, 0, 0))  # Transparent background
                
                text = font.render(symbol, True, color)
                # Center the symbol on the surface
                x = (self.square_size - text.get_width()) // 2
                y = (self.square_size - text.get_height()) // 2
                piece_surface.blit(text, (x, y))
                
                piece_images[piece_type] = piece_surface
        
        return piece_images
    
    def draw(self):
        """Draw the chess board and pieces."""
        # Draw border around the board
        border_width = 3
        pygame.draw.rect(
            self.screen, 
            self.border_color, 
            (
                self.board_offset_x - border_width, 
                self.board_offset_y - border_width,
                self.board_size + border_width * 2, 
                self.board_size + border_width * 2
            )
        )
        
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._draw_coordinates()
    
    def _draw_board(self):
        """Draw the chess board squares."""
        for rank in range(8):
            for file in range(8):
                x = file * self.square_size + self.board_offset_x
                y = (7 - rank) * self.square_size + self.board_offset_y  # Flip for screen coordinates
                
                # Alternate colors for the chess board pattern
                if (rank + file) % 2 == 0:
                    color = self.light_square
                else:
                    color = self.dark_square
                
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
    
    def _draw_highlights(self):
        """Draw highlights for selected square and legal moves."""
        if self.selected_square is not None:
            rank, file = self.selected_square
            x = file * self.square_size + self.board_offset_x
            y = (7 - rank) * self.square_size + self.board_offset_y
            
            # Create a surface with alpha channel for transparency
            highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            # Use a more subtle highlight color similar to lichess
            highlight_surface.fill((255, 255, 0, 60))  # Very light yellow highlight
            self.screen.blit(highlight_surface, (x, y))
        
        # Highlight legal moves
        for move in self.legal_moves:
            from_square, to_square = move
            to_rank, to_file = to_square
            x = to_file * self.square_size + self.board_offset_x
            y = (7 - to_rank) * self.square_size + self.board_offset_y
            
            # Create a surface for the legal move highlight
            move_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            
            # Get the target square piece
            target_piece = self.board.squares[to_rank][to_file]
            
            if target_piece != EMPTY:
                # If capturing, draw a semi-transparent circle around the piece (lichess style)
                pygame.draw.circle(
                    move_surface,
                    (0, 0, 0, 60),  # Semi-transparent dark circle
                    (self.square_size // 2, self.square_size // 2),
                    self.square_size // 2 - 2,
                    width=3  # Draw as a ring
                )
            else:
                # Empty square, draw a dot
                pygame.draw.circle(
                    move_surface, 
                    (0, 0, 0, 80),  # Semi-transparent black
                    (self.square_size // 2, self.square_size // 2), 
                    self.square_size // 8
                )
            
            self.screen.blit(move_surface, (x, y))
    
    def _draw_pieces(self):
        """Draw chess pieces on the board."""
        for rank in range(8):
            for file in range(8):
                piece = self.board.squares[rank][file]
                
                if piece != EMPTY:
                    x = file * self.square_size + self.board_offset_x
                    y = (7 - rank) * self.square_size + self.board_offset_y
                    
                    # Get the piece image
                    piece_img = self.piece_images.get(piece)
                    
                    if piece_img:
                        # Calculate position to center the piece in the square
                        piece_x = x + (self.square_size - piece_img.get_width()) // 2
                        piece_y = y + (self.square_size - piece_img.get_height()) // 2
                        self.screen.blit(piece_img, (piece_x, piece_y))
    
    def _draw_coordinates(self):
        """Draw rank and file coordinates."""
        # Use a larger font size for better visibility
        font = pygame.font.SysFont('Arial', int(self.square_size // 3.5))
        font_bold = pygame.font.SysFont('Arial', int(self.square_size // 3.5), bold=True)
        
        # Draw file coordinates (a-h) at the bottom of the board
        for file in range(8):
            x = file * self.square_size + self.board_offset_x + self.square_size // 2
            y = self.board_offset_y + self.board_size + 25  # More space below board
            
            file_letter = chr(ord('a') + file)
            
            # Always use white text on dark background for better visibility
            text = font_bold.render(file_letter, True, (240, 240, 240))
            # Draw a small circle background for better visibility
            pygame.draw.circle(
                self.screen,
                (60, 60, 60),  # Dark background
                (x, y),
                self.square_size // 6,
                0  # Filled circle
            )
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # Draw rank coordinates (1-8) on the left side of the board
        for rank in range(8):
            x = self.board_offset_x - 25  # More space to the left
            y = (7 - rank) * self.square_size + self.board_offset_y + self.square_size // 2
            
            rank_number = str(rank + 1)
            
            # Always use white text on dark background for better visibility
            text = font_bold.render(rank_number, True, (240, 240, 240))
            # Draw a small circle background for better visibility
            pygame.draw.circle(
                self.screen,
                (60, 60, 60),  # Dark background
                (x, y),
                self.square_size // 6,
                0  # Filled circle
            )
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def set_selected_square(self, square: Optional[Tuple[int, int]]):
        """Set the currently selected square."""
        self.selected_square = square
    
    def set_legal_moves(self, moves: List[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Set the list of legal moves to highlight."""
        self.legal_moves = moves
    
    def screen_to_board_position(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Convert screen coordinates to board position.
        Returns (rank, file) or None if outside the board.
        """
        x, y = pos
        
        # Check if the click is within the board boundaries
        if (x < self.board_offset_x or 
            x >= self.board_offset_x + self.board_size or
            y < self.board_offset_y or
            y >= self.board_offset_y + self.board_size):
            return None
        
        # Convert to file and rank
        file = (x - self.board_offset_x) // self.square_size
        rank = 7 - ((y - self.board_offset_y) // self.square_size)  # Flip for internal representation
        
        return (rank, file) 