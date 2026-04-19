# Go — Neural AI Edition

A complete and fully playable 9×9 Go client built in Python using `pygame` and `PyTorch`. This version features a self-training neural network AI powered by Monte Carlo Tree Search (MCTS), generational self-play training, and a polished dark-themed interface.



---

## Overview

This project recreates the board game Go with a focus on correctness, playability, and a continuously improving AI opponent. It supports multiplayer, neural AI opponents, and a full set of Go mechanics including captures, liberties, suicide prevention, Ko, and Tromp-Taylor end-game scoring.


---

## Installation

Run from source:

```
pip install pygame torch numpy
python go_torch_fixed.py
```

No pre-trained weights are required — the AI will initialise randomly and begin training from scratch. If a `go_torch_weights.pt` file exists in the same directory it will be loaded automatically.

---

## Game Modes

- **Multiplayer** — two human players on the same machine
- **vs AI (Play as Black)** — you play Black, AI plays White
- **vs AI (Play as White)** — AI plays Black (moves first), you play White


---

## AI Architecture

The neural network is a residual convolutional network (ResNet) implemented in PyTorch:

- **Input:** 4-channel 9×9 board representation (own stones, opponent stones, liberties, turn indicator)
- **Backbone:** convolutional input layer → 4 residual blocks → 32 filters each
- **Policy head:** outputs a probability distribution over all 81 board intersections
- **Value head:** outputs a scalar in [-1, 1] estimating the current player's win probability

This architecture is deliberately compact — 32 filters and 4 res blocks is well matched to 9×9 Go and runs efficiently on CPU.

---


### MCTS (Monte Carlo Tree Search)

During play and training, the AI uses MCTS to evaluate positions:

- **600 simulations** per move during play and evaluation
- **UCB (PUCT) selection** balancing exploration and exploitation




---

## Scoring

Tromp-Taylor scoring is used throughout — **no komi**. This means:

- Every stone on the board counts for its owner
- Empty intersections surrounded entirely by one colour count as that colour's territory
- Neutral points (dame) count for neither player
- No points added for White to compensate for Black moving first

---

## Game Rules

### Turns
- Black plays first.
- Players alternate placing stones on empty intersections.

### Liberties
- Stones must have at least one liberty (adjacent empty intersection).
- Groups with no liberties are automatically captured and removed.

### Capturing
The game automatically detects surrounded groups, removes captured stones, and updates scores.

### Illegal Moves
The game prevents:
- Placing on an occupied intersection
- Suicide moves (a move that would leave your own group with no liberties, unless it captures)
- Ko violations (repeating the immediately previous board position)

### Passing and Ending
- Press **Spacebar** to pass.
- The game ends after two consecutive passes.
- Final Tromp-Taylor score is calculated and the winner is displayed.

---

## Controls

| Input | Action |
|-------|--------|
| Left click | Place a stone |
| Spacebar | Pass turn |
| Escape | Quit |

---

## User Interface

- Dark-themed menu with neural AI status indicator
- In-game sidebar showing score, current turn, and AI thinking status
- Adjustable difficulty (simulation count) during play
- Animated last-move marker
- Star points on standard 9×9 hoshi positions
- Game-over overlay with final score


---

## Performance

On a mid-range CPU (e.g. Ryzen 7 7730u):

- ~10-20s per move and never goes into 'not responding'.

---

## Future Improvements

- GPU training support for significantly faster generation times
- 13×13 board size option
- Opening book integration
- Undo during human vs AI games
- Online multiplayer
- SGF export for game records

---

## License

Open for modification and extension.
