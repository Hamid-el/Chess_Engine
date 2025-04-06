# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pygame
import sys
import threading
import time
import os

from src.core.board import Board, WHITE, BLACK
from src.core.game import ChessGame
from src.ai.engine import ChessAI
from src.gui.renderer import BoardRenderer
from src.gui.input_handler import InputHandler
from src.gui.ui_components import Button, Label, Panel, Dropdown, MessageBox

# Constants
SCREEN_WIDTH = 1200  # Even wider to ensure board fits
SCREEN_HEIGHT = 760
BOARD_SIZE = 600
SQUARE_SIZE = BOARD_SIZE // 8
BG_COLOR = (30, 30, 30)  # Darker background for better contrast

class ChessApplication:
    """Main chess application."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chess Engine with AI")
        self.clock = pygame.time.Clock()
        
        # Sound effects
        self.move_sound = None
        self.capture_sound = None
        self._load_sounds()
        
        # Game state
        self.board = Board()
        self.game = ChessGame()
        self.ai = ChessAI(self.game.board, difficulty=3)
        self.ai_thinking = False
        self.player_color = WHITE  # Default player is white, AI is black
        
        # UI components
        self.board_renderer = BoardRenderer(self.screen, self.game.board, SQUARE_SIZE)
        self.input_handler = InputHandler(self.game, self.board_renderer)
        self.input_handler.set_on_move_made(self.on_player_move_made)
        
        # Create UI panels and components
        self._create_ui_components()
        
        # If player is black, make AI move first
        if self.player_color == BLACK:
            self.ai_thinking = True
            threading.Thread(target=self.ai_move, daemon=True).start()
    
    def _create_ui_components(self):
        """Create UI panels and components."""
        # Calculate centered board position
        board_left = (SCREEN_WIDTH - BOARD_SIZE) // 2
                
        # Side panel positioned to the far right to avoid blocking the board
        panel_width = 280
        self.status_panel = Panel(
            SCREEN_WIDTH - panel_width - 20, 20, 
            panel_width, SCREEN_HEIGHT - 40
        )
        
        # Game status label
        self.status_label = Label(
            SCREEN_WIDTH - panel_width, 40, 
            "Game in progress", 24
        )
        
        # Turn indicator
        self.turn_label = Label(
            SCREEN_WIDTH - panel_width, 90, 
            "White to move", 20
        )
        
        # Color selection
        self.color_label = Label(
            SCREEN_WIDTH - panel_width, 140,
            "Play as:", 20
        )
        
        # White button
        self.white_button = Button(
            SCREEN_WIDTH - panel_width, 170,
            (panel_width - 50) // 2, 40,
            "White",
            lambda: self.set_player_color(WHITE)
        )
        
        # Black button
        self.black_button = Button(
            SCREEN_WIDTH - panel_width + (panel_width - 50) // 2 + 10, 170,
            (panel_width - 50) // 2, 40,
            "Black",
            lambda: self.set_player_color(BLACK)
        )
        
        # AI difficulty dropdown
        self.difficulty_label = Label(
            SCREEN_WIDTH - panel_width, 230, 
            "AI Difficulty:", 20
        )
        
        self.difficulty_dropdown = Dropdown(
            SCREEN_WIDTH - panel_width, 260, 
            panel_width - 40, 40,
            ["Easy (Depth 2)", "Medium (Depth 3)", "Hard (Depth 4)", "Expert (Depth 5)"],
            self.on_difficulty_changed
        )
        
        # AI algorithm options
        self.algorithm_label = Label(
            SCREEN_WIDTH - panel_width, 320, 
            "AI Algorithm:", 20
        )
        
        # Use neural network button
        self.nn_button = Button(
            SCREEN_WIDTH - panel_width, 350, 
            panel_width - 40, 45,
            "Use Neural Network", 
            self.toggle_neural_network
        )
        
        # Use bitboards button
        self.bitboard_button = Button(
            SCREEN_WIDTH - panel_width, 405, 
            panel_width - 40, 45,
            "Use Bitboards", 
            self.toggle_bitboards
        )
        
        # New game button
        self.new_game_button = Button(
            SCREEN_WIDTH - panel_width, 470, 
            panel_width - 40, 50,
            "New Game", 
            self.new_game
        )
        
        # Undo move button
        self.undo_button = Button(
            SCREEN_WIDTH - panel_width, 530, 
            panel_width - 40, 50,
            "Undo Move", 
            self.undo_move
        )
        
        # Add components to panel
        self.status_panel.add_component(self.status_label)
        self.status_panel.add_component(self.turn_label)
        self.status_panel.add_component(self.color_label)
        self.status_panel.add_component(self.white_button)
        self.status_panel.add_component(self.black_button)
        self.status_panel.add_component(self.difficulty_label)
        self.status_panel.add_component(self.difficulty_dropdown)
        self.status_panel.add_component(self.algorithm_label)
        self.status_panel.add_component(self.nn_button)
        self.status_panel.add_component(self.bitboard_button)
        self.status_panel.add_component(self.new_game_button)
        self.status_panel.add_component(self.undo_button)
        
        # Message box for game over (initially not visible)
        self.message_box = None
    
    def _load_sounds(self):
        """Load sound effects from assets directory."""
        try:
            # Initialize the mixer
            pygame.mixer.init()
            
            # Load move sound
            move_sound_path = os.path.join("assets", "audio", "Move.mp3")
            self.move_sound = pygame.mixer.Sound(move_sound_path)
            self.move_sound.set_volume(0.4)
            
            # Load capture sound
            capture_sound_path = os.path.join("assets", "audio", "Capture.mp3")
            self.capture_sound = pygame.mixer.Sound(capture_sound_path)
            self.capture_sound.set_volume(0.4)
            
            print("Successfully loaded sound effects")
        except Exception as e:
            print(f"Error loading sound effects: {e}")
    
    def _play_move_sound(self, is_capture=False):
        """Play the appropriate move sound."""
        if is_capture and self.capture_sound:
            self.capture_sound.play()
        elif self.move_sound:
            self.move_sound.play()
    
    def on_difficulty_changed(self, difficulty_text):
        """Handle difficulty dropdown selection."""
        if "Easy" in difficulty_text:
            self.ai.set_difficulty(2)
        elif "Medium" in difficulty_text:
            self.ai.set_difficulty(3)
        elif "Hard" in difficulty_text:
            self.ai.set_difficulty(4)
        elif "Expert" in difficulty_text:
            self.ai.set_difficulty(5)
    
    def toggle_neural_network(self):
        """Toggle neural network usage."""
        currently_using_nn = self.ai.use_neural_network
        self.ai.toggle_neural_network(not currently_using_nn)
        
        # Update button text
        self.nn_button.text = "Traditional Evaluation" if self.ai.use_neural_network else "Use Neural Network"
        
        # If neural network is enabled, disable bitboards
        if self.ai.use_neural_network:
            self.bitboard_button.text = "Use Bitboards"
    
    def toggle_bitboards(self):
        """Toggle bitboard usage."""
        currently_using_bb = self.ai.use_bitboards
        self.ai.toggle_bitboards(not currently_using_bb)
        
        # Update button text
        self.bitboard_button.text = "Traditional Search" if self.ai.use_bitboards else "Use Bitboards"
        
        # If bitboards are enabled, disable neural network
        if self.ai.use_bitboards:
            self.nn_button.text = "Use Neural Network"
    
    def set_player_color(self, color):
        """Set the player's color (WHITE or BLACK)."""
        # Only allow changing color when not in the middle of a game
        if self.ai_thinking or len(self.game.board.move_history) > 0:
            return
            
        self.player_color = color
        
        # Highlight the selected button
        if color == WHITE:
            self.white_button.bg_color = (150, 200, 150)  # Green highlight
            self.black_button.bg_color = None  # Default color
        else:
            self.white_button.bg_color = None  # Default color
            self.black_button.bg_color = (150, 200, 150)  # Green highlight
            
        # Start a new game with the selected color
        self.new_game()
    
    def new_game(self):
        """Start a new game."""
        self.board = Board()
        self.game = ChessGame()
        self.ai.set_board(self.game.board)
        self.board_renderer = BoardRenderer(self.screen, self.game.board, SQUARE_SIZE)
        self.input_handler = InputHandler(self.game, self.board_renderer)
        self.input_handler.set_on_move_made(self.on_player_move_made)
        
        # Update status
        self.status_label.set_text("Game in progress")
        self.turn_label.set_text("White to move")
        
        # Hide game over message box if visible
        if self.message_box:
            self.message_box.visible = False
            
        # If player is black, make AI move first
        if self.player_color == BLACK:
            self.ai_thinking = True
            threading.Thread(target=self.ai_move, daemon=True).start()
    
    def undo_move(self):
        """Undo the last two moves (player and AI)."""
        # Undo AI move
        self.game.undo_move()
        # Undo player move
        self.game.undo_move()
        
        # Update turn indicator
        self.turn_label.set_text("White to move" if self.board.side_to_move == 0 else "Black to move")
    
    def on_player_move_made(self):
        """Called when the player makes a move."""
        # Play the move sound (check if it was a capture by looking at the last move)
        last_move = self.game.board.move_history[-1] if self.game.board.move_history else None
        is_capture = False
        if last_move:
            _, captured_piece = last_move
            is_capture = captured_piece != 0  # Check if captured piece is not EMPTY
        self._play_move_sound(is_capture)
        
        # Update turn indicator
        self.turn_label.set_text("Black to move" if self.game.board.side_to_move == BLACK else "White to move")
        
        # Check for game over
        if self.game.is_game_over():
            self.show_game_over_message()
            return
        
        # Start AI thinking in a separate thread (only if it's AI's turn)
        if (self.player_color == WHITE and self.game.board.side_to_move == BLACK) or \
           (self.player_color == BLACK and self.game.board.side_to_move == WHITE):
            self.ai_thinking = True
            threading.Thread(target=self.ai_move, daemon=True).start()
    
    def ai_move(self):
        """Make AI move in a separate thread."""
        try:
            # Add a small delay for better UX
            time.sleep(0.5)
            
            # Get AI move without updating the visual board (internal calculation only)
            move = self.ai.get_move()
            
            if move:
                # Now make the move on the game board
                self.game.make_move(*move)
                
                # Play the move sound
                is_capture = False
                if self.game.board.move_history:
                    _, captured_piece = self.game.board.move_history[-1]
                    is_capture = captured_piece != 0
                self._play_move_sound(is_capture)
                
                # Update turn indicator
                self.turn_label.set_text("White to move" if self.game.board.side_to_move == WHITE else "Black to move")
                
                # Check for game over
                if self.game.is_game_over():
                    self.show_game_over_message()
        finally:
            self.ai_thinking = False
    
    def show_game_over_message(self):
        """Show game over message."""
        game_state, winner = self.game.get_game_result()
        
        if game_state == "checkmate":
            message = f"Checkmate! {'White' if winner == 'white' else 'Black'} wins!"
        elif game_state == "stalemate":
            message = "Stalemate! The game is a draw."
        else:
            message = f"Game over! {game_state.capitalize()}."
        
        self.status_label.set_text(message)
        self.message_box = MessageBox(SCREEN_WIDTH, SCREEN_HEIGHT, message)
    
    def run(self):
        """Main application loop."""
        running = True
        previous_board_state = None
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle UI events
                if self.message_box and self.message_box.visible:
                    self.message_box.handle_event(event)
                elif not self.ai_thinking:
                    if not self.status_panel.handle_event(event):
                        self.input_handler.handle_event(event)
            
            # Clear screen
            self.screen.fill(BG_COLOR)
            
            # When AI is thinking, freeze the board display
            if self.ai_thinking:
                # If we have a stored previous state, use it instead of the current board
                if previous_board_state is None:
                    # Store current board state before AI starts thinking
                    previous_board_state = self.game.board.get_copy()
                
                # Create a temporary renderer with the previous board state
                temp_renderer = BoardRenderer(self.screen, previous_board_state, SQUARE_SIZE)
                temp_renderer.draw()
            else:
                # AI is not thinking, display current board
                previous_board_state = None
                self.board_renderer.draw()
            
            # Draw UI panels
            self.status_panel.draw(self.screen)
            
            # Draw "AI Thinking" message if applicable
            if self.ai_thinking:
                font = pygame.font.SysFont('Arial', 24)
                text = font.render("AI is thinking...", True, (255, 255, 255))
                self.screen.blit(text, (BOARD_SIZE // 2 - 80, 10))
            
            # Draw message box if visible
            if self.message_box and self.message_box.visible:
                self.message_box.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            
            # Cap framerate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = ChessApplication()
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
