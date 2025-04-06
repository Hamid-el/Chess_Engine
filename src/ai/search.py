import random
import time
from typing import Tuple, Optional, List, Dict
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.core.board import Board
from src.core.move_generator import MoveGenerator
from src.ai.evaluation import Evaluator

class AlphaBetaSearch:
    """Alpha-beta pruning search algorithm for finding the best move."""
    
    def __init__(self, board: Board, evaluator: Evaluator):
        self.board = board
        self.evaluator = evaluator
        self.move_generator = MoveGenerator(board)
        self.transposition_table = {}  # For storing previously evaluated positions
        self.nodes_searched = 0
        self.start_time = 0
        self.time_limit = 0  # Time limit in seconds
        
    def search(self, depth: int, time_limit: float = 5.0) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Search for the best move using alpha-beta pruning.
        Returns the best move as (from_square, to_square).
        """
        self.nodes_searched = 0
        self.start_time = time.time()
        self.time_limit = time_limit
        
        # Initialize alpha and beta values for alpha-beta pruning
        alpha = float('-inf')
        beta = float('inf')
        
        best_move = None
        best_value = float('-inf')
        
        # Get all legal moves
        legal_moves = self.move_generator.get_legal_moves()
        
        # If there are no legal moves, return None
        if not legal_moves:
            return None
        
        # Try each move and select the best one
        for move in legal_moves:
            # Make the move
            self.board.make_move(move)
            
            # Search the resulting position
            value = -self._alpha_beta(depth - 1, -beta, -alpha, False)
            
            # Undo the move
            self.board.undo_move()
            
            # Update best move if necessary
            if value > best_value:
                best_value = value
                best_move = move
            
            # Update alpha
            alpha = max(alpha, value)
            
            # Check if time limit is exceeded
            if time.time() - self.start_time > self.time_limit:
                break
        
        print(f"Nodes searched: {self.nodes_searched}")
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
        
        # Check for draw or checkmate
        if self.board.is_game_over():
            # Adjust for distance to checkmate
            if self._is_checkmate():
                return -100000 if is_maximizing else 100000
            return 0  # Draw
        
        # Reached maximum depth, evaluate position
        if depth == 0:
            return self.evaluator.evaluate(self.board)
        
        # Generate moves
        legal_moves = self.move_generator.get_legal_moves()
        
        # Sort moves (move ordering for better pruning)
        # In a full implementation, capture moves would be tried first
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                self.board.make_move(move)
                eval = self._alpha_beta(depth - 1, alpha, beta, False)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                self.board.make_move(move)
                eval = self._alpha_beta(depth - 1, alpha, beta, True)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    def _is_checkmate(self) -> bool:
        """Check if the current position is checkmate."""
        return len(self.move_generator.get_legal_moves()) == 0 and \
               self.move_generator._is_king_in_check(self.board.side_to_move)


class NeuralNetwork(nn.Module):
    """Neural network for position evaluation."""
    
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        
        # Input layer: 12 piece types * 64 squares = 768 inputs (one-hot encoded)
        # 6 piece types for each color (pawn, knight, bishop, rook, queen, king)
        
        # Hidden layers
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 64)
        
        # Output layer: 1 for position evaluation
        self.output = nn.Linear(64, 1)
        
    def forward(self, x):
        """Forward pass."""
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = torch.tanh(self.output(x))  # Output between -1 and 1
        
        # Scale to a reasonable evaluation range (-1000 to 1000)
        x = x * 1000
        
        return x


class NeuralNetworkSearch:
    """Search algorithm that uses a neural network for position evaluation."""
    
    def __init__(self, board: Board):
        self.board = board
        self.move_generator = MoveGenerator(board)
        self.model = NeuralNetwork()
        
        # Try to load a pre-trained model
        try:
            self.model.load_state_dict(torch.load('assets/common/nn_model.pth'))
            self.model.eval()
            print("Loaded neural network model from assets/common/nn_model.pth")
        except Exception as e:
            print(f"Could not load neural network model: {e}")
        
    def search(self, depth: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Search for the best move using the neural network."""
        best_move = None
        best_value = float('-inf')
        
        # Get all legal moves
        legal_moves = self.move_generator.get_legal_moves()
        
        # If there are no legal moves, return None
        if not legal_moves:
            return None
        
        # Try each move and select the best one
        for move in legal_moves:
            # Make the move
            self.board.make_move(move)
            
            # Evaluate the position with minimax using the neural network
            value = -self._minimax(depth - 1, False)
            
            # Undo the move
            self.board.undo_move()
            
            # Update best move if necessary
            if value > best_value:
                best_value = value
                best_move = move
        
        return best_move
    
    def _minimax(self, depth: int, is_maximizing: bool) -> float:
        """
        Minimax search algorithm using the neural network for evaluation.
        Returns the evaluation of the position.
        """
        # Check for draw or checkmate
        if self.board.is_game_over():
            # Adjust for distance to checkmate
            if self._is_checkmate():
                return -100000 if is_maximizing else 100000
            return 0  # Draw
        
        # Reached maximum depth, evaluate position using the neural network
        if depth == 0:
            return self._evaluate_with_nn()
        
        # Generate moves
        legal_moves = self.move_generator.get_legal_moves()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                self.board.make_move(move)
                eval = self._minimax(depth - 1, False)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                self.board.make_move(move)
                eval = self._minimax(depth - 1, True)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
            return min_eval
    
    def _evaluate_with_nn(self) -> float:
        """Evaluate the position using the neural network."""
        # Convert board state to input tensor
        input_tensor = self._board_to_tensor()
        
        # Predict position evaluation
        with torch.no_grad():
            output = self.model(input_tensor)
        
        # Adjust for the side to move
        if self.board.side_to_move == 1:  # BLACK
            return -output.item()
        return output.item()
    
    def _board_to_tensor(self) -> torch.Tensor:
        """Convert board state to input tensor."""
        # Create a tensor of shape (1, 768) - 12 piece types on 64 squares
        input_tensor = torch.zeros(1, 768)
        
        # Fill the tensor with the board state
        for rank in range(8):
            for file in range(8):
                piece = self.board.squares[rank][file]
                if piece == 0:
                    continue
                
                # Calculate the index in the tensor
                piece_type = abs(piece) - 1  # 0-5 for piece types
                if piece < 0:
                    piece_type += 6  # 6-11 for black pieces
                
                # Set the corresponding position to 1
                index = piece_type * 64 + rank * 8 + file
                input_tensor[0, index] = 1
        
        return input_tensor
    
    def _is_checkmate(self) -> bool:
        """Check if the current position is checkmate."""
        return len(self.move_generator.get_legal_moves()) == 0 and \
               self.move_generator._is_king_in_check(self.board.side_to_move) 