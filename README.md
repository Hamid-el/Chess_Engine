# Chess Engine with AI

A complete chess application with a graphical user interface and AI opponent using both traditional search techniques and neural network evaluation.

## Features

- Complete chess rules implementation (legal moves, castling, en passant, etc.)
- Graphical user interface with drag-and-drop piece movement
- AI opponent with adjustable difficulty levels
- Two AI evaluation options:
  - Traditional evaluation with alpha-beta pruning
  - Neural network evaluation (when trained model is available)
- Game state tracking (checkmate, stalemate, draws)
- Move history and undo functionality

## Project Structure

```
chess-engine/
├── src/
│   ├── core/           # Core chess logic
│   │   ├── board.py
│   │   ├── game.py
│   │   └── move_generator.py
│   ├── ai/             # AI implementation
│   │   ├── engine.py
│   │   ├── evaluation.py
│   │   └── search.py
│   └── gui/            # All GUI-related code
│       ├── renderer.py
│       ├── input_handler.py
│       └── ui_components.py
├── assets/             # Chess-specific assets
│   ├── pieces/         # Chess piece images
│   ├── boards/         # Board textures
│   ├── sounds/         # Game sounds
│   └── common/         # Non-GUI specific assets
├── gui/                # GUI-specific assets
│   └── assets/         
│       ├── buttons/
│       ├── backgrounds/
│       └── icons/
├── main.py             # Application entry point
├── firstAI.py          # Original implementation (for reference)
└── requirements.txt    # Project dependencies
```

## Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

Controls:
- Click and drag to move pieces
- Use the difficulty dropdown to adjust AI strength
- Click "Undo Move" to take back your last move
- Press ESC to cancel a selected piece
- Press 'u' to undo a move

## AI Implementation

The AI uses two evaluation methods:

1. **Traditional Evaluation**: A handcrafted evaluation function using material value, piece positions, and other chess heuristics with alpha-beta pruning search.

2. **Neural Network Evaluation**: A deep neural network that evaluates board positions. To use this feature, place a trained model file at `assets/common/nn_model.pth`.

## Requirements

- Python 3.7+
- PyGame 2.5.2
- NumPy 1.26.3
- PyTorch 2.1.2
- python-chess 1.999

## License

MIT

## Acknowledgments

- Original implementation (firstAI.py) by [Original Author]
- Chess piece assets from [Asset Source]
