from typing import Tuple, Optional
from src.core.board import Board
from src.ai.evaluation import Evaluator
from src.ai.search import AlphaBetaSearch, NeuralNetworkSearch

# Import new bitboard classes
from src.core.bitboard import BitBoard
from src.ai.bitboard_search import BitboardSearch

class ChessAI:
    """Chess AI engine that makes moves based on position evaluation and search."""
    
    def __init__(self, board: Board, use_neural_network: bool = False, use_bitboards: bool = False, difficulty: int = 3):
        """
        Initialize the chess AI.
        
        Args:
            board: The chess board
            use_neural_network: Whether to use the neural network for evaluation
            use_bitboards: Whether to use bitboards for faster search
            difficulty: The search depth (higher = stronger, but slower)
        """
        self.board = board
        self.use_neural_network = use_neural_network
        self.use_bitboards = use_bitboards
        self.difficulty = difficulty
        
        # Create evaluator
        self.evaluator = Evaluator()
        
        # Create appropriate search engine
        if use_bitboards:
            # Convert normal board to bitboard
            self.bitboard = BitBoard.from_array(board.squares)
            self.search_engine = BitboardSearch(self.bitboard)
        elif use_neural_network:
            self.search_engine = NeuralNetworkSearch(board)
        else:
            self.search_engine = AlphaBetaSearch(board, self.evaluator)
    
    def get_move(self, time_limit: float = 1.0) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get the best move according to the AI.
        
        Args:
            time_limit: Maximum time to search (in seconds)
            
        Returns:
            The best move as (from_square, to_square) or None if no move is found
        """
        if self.use_bitboards:
            # Get move from bitboard search
            move = self.search_engine.search(self.difficulty, time_limit)
            if move:
                from_square, to_square = move
                # Convert square indices to (rank, file) coordinates
                from_coords = (from_square // 8, from_square % 8)
                to_coords = (to_square // 8, to_square % 8)
                return (from_coords, to_coords)
            return None
        elif self.use_neural_network:
            return self.search_engine.search(self.difficulty)
        else:
            return self.search_engine.search(self.difficulty, time_limit)
    
    def set_difficulty(self, difficulty: int):
        """Set the AI difficulty (search depth)."""
        self.difficulty = difficulty
    
    def set_board(self, board: Board):
        """Update the board reference."""
        self.board = board
        if self.use_bitboards:
            self.bitboard = BitBoard.from_array(board.squares)
            self.search_engine = BitboardSearch(self.bitboard)
        elif self.use_neural_network:
            self.search_engine = NeuralNetworkSearch(board)
        else:
            self.search_engine = AlphaBetaSearch(board, self.evaluator)
    
    def toggle_neural_network(self, use_nn: bool):
        """Toggle using the neural network for evaluation."""
        if use_nn != self.use_neural_network:
            self.use_neural_network = use_nn
            if use_nn:
                self.use_bitboards = False  # Can't use both
                self.search_engine = NeuralNetworkSearch(self.board)
            else:
                if self.use_bitboards:
                    self.bitboard = BitBoard.from_array(self.board.squares)
                    self.search_engine = BitboardSearch(self.bitboard)
                else:
                    self.search_engine = AlphaBetaSearch(self.board, self.evaluator)
    
    def toggle_bitboards(self, use_bb: bool):
        """Toggle using bitboards for move generation and search."""
        if use_bb != self.use_bitboards:
            self.use_bitboards = use_bb
            if use_bb:
                self.use_neural_network = False  # Can't use both
                self.bitboard = BitBoard.from_array(self.board.squares)
                self.search_engine = BitboardSearch(self.bitboard)
            else:
                if self.use_neural_network:
                    self.search_engine = NeuralNetworkSearch(self.board)
                else:
                    self.search_engine = AlphaBetaSearch(self.board, self.evaluator) 