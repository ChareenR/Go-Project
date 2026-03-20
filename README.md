# Go

A complete and fully playable 9×9 Go client built in Python using `pygame`. This version includes full rule enforcement, automatic scoring, multiple game modes, and a Monte Carlo Tree Search (MCTS) AI.

This is the latest fully working version of the game.


## Overview

This project recreates the board game Go with a focus on correctness, clarity, and playability. It supports multiplayer, AI opponents, and a full set of Go mechanics including captures, liberties, suicide prevention, Ko, and end‑game scoring. The interface includes a main menu, instructions screen, in‑game UI, and a game‑over screen.

Players can choose to play against the AI as either Black or White, or play locally with another human.


## Installation

To run the game locally:

1. Download the executable file named First Real Project.exe.
2. Open the file to launch the game.
3. The program will start at the main menu.

To run from source:

```
pip install pygame
python main.py
```


## Game Modes

- Multiplayer (two human players)
- VS AI (Play as Black)
- VS AI (Play as White)
- In‑game AI toggle: Off → AI White → AI Black



## AI (Monte Carlo Tree Search)

The AI uses Monte Carlo Tree Search to evaluate moves. Features include:

- Dynamic iteration count (800, 500, or 300 depending on board complexity)
- Capture‑aware rollouts
- Ko‑safe simulations
- Fallback to a random legal move if no MCTS result is found
- On‑screen indicator showing when the AI is thinking


## Game Rules

### Turns
- Black plays first.
- Players alternate placing stones on empty intersections.

### Liberties
- Stones must have at least one liberty (up, down, left, or right).
- Groups with no liberties are automatically removed.

### Capturing
The program automatically:
- Detects surrounded groups
- Removes captured stones
- Adds captured stones to the player's score

### Illegal Moves
The game prevents:
- Placing a stone on an occupied point
- Suicide moves (unless the move captures)
- Ko violations (repeating the previous board position)

### Passing and Ending the Game
- Press the spacebar to pass your turn.
- The game ends after two consecutive passes.
- The program then calculates the final score and displays the winner.


## Scoring

The scoring system includes:
- Territory detection
- Stone count
- Captured stones
- Automatic score calculation at the end of the game


## Controls

- Left click: Place a stone
- Spacebar: Pass turn
- Escape: Quit to menu
- Mouse click: Navigate menu buttons



## User Interface Features

- Main menu with four options: Multiplayer, VS AI (Black), VS AI (White), How to Play
- Instructions screen explaining rules and controls
- In‑game UI showing turn, score, and AI status
- Last move marker
- Star points on the board
- Pass notification
- Game‑over screen with final score and return button



## Technical Features

- Full board state tracking
- Group detection and liberty counting
- Deep copies for simulations
- Ko enforcement using previous board comparison
- Debug output for moves, passes, and AI decisions
- Frame rate control for consistent rendering
- Error handling for invalid moves


## Future Improvements

- Undo and redo system
- Additional board sizes (13×13, 19×19)
- Sound effects and animations
- Online multiplayer


## License

This project is open for modification and extension.

