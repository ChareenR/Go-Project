
 Go-Project  
A Python recreation of the classic board game Go, built using `pygame`.  
This is the latest fully working version of the game.

 Overview  
This project implements a playable 9×9 version of Go, including capturing, liberties, illegal move detection, and optional Ko rule support.  The goal is to provide a clean, beginner‑friendly implementation of Go’s core mechanics. You may play against the AI as either color (this uses Monte Carlo Tree Search to find the optimal move) or you can play against a friend in multiplayer.

Installation  
To run the game locally:

1. Download First Real Project.exe and open the file.
2. This will run the file to a start menu.
3. Enjoy!


Rules of the Game

Turns
- The game is played by two players on a **9×9 grid**  
- Black plays first  
- White plays second  
- Players alternate placing one stone on any empty intersection


Liberties
- Every stone has *liberties*: empty spaces directly **up, down, left, or right**
- Stones with at least one liberty remain on the board
- Stones with zero liberties are automatically captured and removed by the program


Capturing
- If you place a stone that removes the last liberty of an opponent’s connected group, that group is captured
- The program automatically:
  - Detects captures  
  - Removes captured stones  
  - Adds captured stones to your score  


Illegal Moves
The program prevents:
- Placing a stone on an **occupied** point  
- **Suicide moves** (placing a stone that would have zero liberties *and* does not capture anything)

If a move is illegal, nothing is placed.


Ko Rule
- You cannot play a move that recreates the **exact previous board position**  
- If attempted, the program blocks the move

 Ending the Game
The game ends when:
- Both players pass, or  
- Players manually decide to stop  -- if playing against AI and it passes twice, you may press spacebar to end the game.

To pass your turn, press Spacebar.

More detailed rules can be found in the How to Play section inside the program.


Controls

 Place stone --> Left-click 
 Pass turn --> Spacebar 
Quit game --> ESC 


 Features
- Full liberty and capture detection  
- Suicide move prevention  
- Ko rule  
- Capture scoring  
- Clean 9×9 board rendering  
- Simple, intuitive controls  



Future Improvements (Ideas)  
- Add 13×13 and 19×19 board sizes    
- Add undo/redo  
- Add sound effects and animations  
- Add online multiplayer  



License  
Feel free to modify or expand this project.

