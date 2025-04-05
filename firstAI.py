import pygame
import chess
import threading
import time
import random
import os

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 560, 560
BOARD_SIZE = 480
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
LIGHT_SQUARE = (220, 184, 140)  # Light brown
DARK_SQUARE = (166, 109, 79)  # Dark brown
HIGHLIGHT = (70, 130, 180, 128)  # Steelblue with some transparency
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (40, 40, 40)

# Material values for simple evaluation
MATERIAL_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King's value is not considered
}


def evaluate_board(board):
    """material evaluation: Positive for White, negative for Black."""
    evaluation = 0
    for piece_type in MATERIAL_VALUES:
        evaluation += (len(board.pieces(piece_type, chess.WHITE)) - len(board.pieces(piece_type, chess.BLACK))) * \
                      MATERIAL_VALUES[piece_type]
    return evaluation


def minimax(board, depth, is_maximizing):
    """Minimax algorithm without Alpha-Beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if is_maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move


class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Engine with AI")

        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.piece_images = self.load_piece_images()

        # Offset for centering the board
        self.board_offset_x = (WIDTH - BOARD_SIZE) // 2
        self.board_offset_y = (HEIGHT - BOARD_SIZE) // 2

        # Game state
        self.game_over = False
        self.message = ""

        # Initialize the font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)

    def load_piece_images(self):
        """Load chess piece images. If not available, draw symbols."""
        piece_images = {}
        piece_chars = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # black
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'  # white
        }

        # Using symbols as we don't have image files
        font = pygame.font.SysFont('Arial', 40)
        for piece, char in piece_chars.items():
            color = WHITE if piece.isupper() else BLACK
            text_surface = font.render(char, True, color)
            piece_images[piece] = text_surface

        return piece_images

    def draw_board(self):
        self.screen.fill(BACKGROUND) # Draw background

        # Draw board squares
        for rank in range(8):
            for file in range(8):
                x = file * SQUARE_SIZE + self.board_offset_x
                y = rank * SQUARE_SIZE + self.board_offset_y
                color = LIGHT_SQUARE if (file + rank) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        # Draw rank and file labels
        font = pygame.font.SysFont('Arial', 16)
        for i in range(8):
            # Ranks (1-8)
            rank_label = font.render(str(8 - i), True, WHITE)
            self.screen.blit(rank_label,
                             (self.board_offset_x - 20, i * SQUARE_SIZE + self.board_offset_y + SQUARE_SIZE // 2 - 8))

            # Files (a-h)
            file_label = font.render(chr(97 + i), True, WHITE)
            self.screen.blit(file_label, (i * SQUARE_SIZE + self.board_offset_x + SQUARE_SIZE // 2 - 4,
                                          self.board_offset_y + BOARD_SIZE + 10))

    def draw_pieces(self):
        """Draw the chess pieces on the board."""
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)  # Flip rank for drawing
                piece = self.board.piece_at(square)
                if piece:
                    x = file * SQUARE_SIZE + self.board_offset_x + SQUARE_SIZE // 2
                    y = rank * SQUARE_SIZE + self.board_offset_y + SQUARE_SIZE // 2
                    piece_img = self.piece_images[piece.symbol()]
                    # Center the piece image on the square
                    self.screen.blit(piece_img, (x - piece_img.get_width() // 2, y - piece_img.get_height() // 2))

    def highlight_selected_square(self):
        """Highlight the selected square."""
        if self.selected_square is not None:
            file = chess.square_file(self.selected_square)
            rank = 7 - chess.square_rank(self.selected_square)  # Flip rank for drawing
            x = file * SQUARE_SIZE + self.board_offset_x
            y = rank * SQUARE_SIZE + self.board_offset_y

            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT)
            self.screen.blit(highlight_surface, (x, y))

            # Also highlight legal moves
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    target_file = chess.square_file(move.to_square)
                    target_rank = 7 - chess.square_rank(move.to_square)
                    target_x = target_file * SQUARE_SIZE + self.board_offset_x
                    target_y = target_rank * SQUARE_SIZE + self.board_offset_y

                    # Draw a circle for legal moves
                    target_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(target_surface, HIGHLIGHT, (SQUARE_SIZE // 2, SQUARE_SIZE // 2),
                                       SQUARE_SIZE // 6)
                    self.screen.blit(target_surface, (target_x, target_y))

    def draw_status(self):
        """Draw game status message."""
        if self.ai_thinking:
            message = "AI is thinking..."
        elif self.game_over:
            message = self.message
        else:
            message = "White's turn" if self.board.turn == chess.WHITE else "Black's turn"

        text = self.font.render(message, True, WHITE)
        self.screen.blit(text, (10, 10))

    def screen_to_board_position(self, pos):
        """Convert screen position to board position."""
        x, y = pos
        if (x < self.board_offset_x or x >= self.board_offset_x + BOARD_SIZE or
                y < self.board_offset_y or y >= self.board_offset_y + BOARD_SIZE):
            return None  # Click outside the board

        file = (x - self.board_offset_x) // SQUARE_SIZE
        rank = 7 - (y - self.board_offset_y) // SQUARE_SIZE  # Flip rank for calculation
        return chess.square(file, rank)

    def handle_click(self, pos):
        """Handle mouse click events."""
        if self.ai_thinking or self.game_over or self.board.turn == chess.BLACK:
            return

        square = self.screen_to_board_position(pos)
        if square is None:
            return

        if self.selected_square is None:
            # First click - selecting a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
        else:
            # Second click - make a move
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                # Check game state after the move
                self.check_game_state()
                if not self.game_over:
                    # Start AI move in a separate thread
                    self.ai_thinking = True
                    threading.Thread(target=self.ai_move, daemon=True).start()
            # Reset selection regardless
            self.selected_square = None

    def ai_move(self):
        """Calculate and make AI move."""
        try:
            time.sleep(0.5)  # Short pause for better UX
            _, move = minimax(self.board, depth=2, is_maximizing=False)

            # If no move is found (in case of checkmate, etc.), try to find a legal move
            if move is None:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    move = random.choice(legal_moves)

            if move:
                self.board.push(move)
                self.check_game_state()
        finally:
            self.ai_thinking = False

    def check_game_state(self):
        """Check if the game is over."""
        if self.board.is_checkmate():
            self.game_over = True
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            self.message = f"Checkmate! {winner} wins!"
        elif self.board.is_stalemate():
            self.game_over = True
            self.message = "Stalemate!"
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.message = "Draw by insufficient material!"
        elif self.board.is_fifty_moves():
            self.game_over = True
            self.message = "Draw by fifty-move rule!"
        elif self.board.is_repetition():
            self.game_over = True
            self.message = "Draw by threefold repetition!"

    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game with 'r' key
                        self.board = chess.Board()
                        self.selected_square = None
                        self.game_over = False
                        self.message = ""

            # Draw everything
            self.draw_board()
            self.highlight_selected_square()
            self.draw_pieces()
            self.draw_status()

            pygame.display.flip()
            clock.tick(30)  # 30 FPS

        pygame.quit()


if __name__ == "__main__":
    game = ChessGame()
    game.run()