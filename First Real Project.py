import pygame, sys
from pygame.locals import *
import numpy as np
from random import randint
import math
import copy
from collections import defaultdict



class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = board 
        self.player = player  
        self.parent = parent
        self.move = move  
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self.get_legal_moves()
    
    def get_legal_moves(self):
        
        moves = []
        for r in range(Board_size):
            for c in range(Board_size):
                if self.board[r][c] == EMPTY:
                    # Check if move is legal
                    _, _, valid, _, _ = make_move(self.board, r, c, self.player, None)
                    if valid:
                        moves.append((r, c))
        return moves
    
    def ucb1(self, total_visits, exploration=1.41):
     
        if self.visits == 0:
            return float('inf')
        return self.wins/self.visits + exploration * math.sqrt(math.log(total_visits)/self.visits)
    
    def best_child(self, exploration=1.41):
        
        total_visits = sum(child.visits for child in self.children)
        return max(self.children, key=lambda c: c.ucb1(total_visits, exploration))
    
    def expand(self):
        
        move = self.untried_moves.pop()
        new_board, captured, valid, _, _ = make_move(self.board, move[0], move[1], self.player, None)
        next_player = WHITE if self.player == BLACK else BLACK
        child = MCTSNode(new_board, next_player, parent=self, move=move)
        self.children.append(child)
        return child
    
    def rollout(self):
        """Simulate a random game from this node with capture tracking"""
        current_board = copy.deepcopy(self.board)
        current_player = self.player
        move_count = 0
        max_moves = Board_size * Board_size * 2  # Prevent infinite loops
        
        # Track captures during simulation
        sim_black_captures = 0
        sim_white_captures = 0
        
        while move_count < max_moves:
            # Get legal moves
            moves = []
            for r in range(Board_size):
                for c in range(Board_size):
                    if current_board[r][c] == EMPTY:
                        _, _, valid, _, _ = make_move(current_board, r, c, current_player, None)
                        if valid:
                            moves.append((r, c))
            
            if not moves:
                # No moves - pass
                current_player = WHITE if current_player == BLACK else BLACK
                move_count += 1
                continue
            
            # Make random move
            move = moves[randint(0, len(moves)-1)]
            new_board, captured, valid, _, _ = make_move(current_board, move[0], move[1], current_player, None)
            
            if valid:
                # Track captures
                if captured > 0:
                    if current_player == BLACK:
                        sim_black_captures += captured
                    else:
                        sim_white_captures += captured
                
                current_board = new_board
                current_player = WHITE if current_player == BLACK else BLACK
                move_count += 1
        
        # Calculate final score including captures
        black_score, white_score = compute_score(current_board, 0, 0)
        black_score += sim_black_captures
        white_score += sim_white_captures
        
        if black_score > white_score:
            return BLACK
        elif white_score > black_score:
            return WHITE
        else:
            return None  # Draw
    
    def backpropagate(self, result):
        
        self.visits += 1
        if result == self.player:
            self.wins += 1
        elif result is None:  
            self.wins += 0.5
        if self.parent:
            self.parent.backpropagate(result)

def monte_carlo_search(root_board, player, iterations=1000):
    """Main MCTS function"""
    root = MCTSNode(root_board, player)
    
    for _ in range(iterations):
       
        node = root
        while node.children and not node.untried_moves:
            node = node.best_child()
        
        
        if node.untried_moves:
            node = node.expand()
        
        
        result = node.rollout()
        
        
        node.backpropagate(result)
    
    
    if root.children:
       
        best = max(root.children, key=lambda c: c.visits)
        return best.move
    else:
        return None  


EMPTY = 0
BLACK = 1
WHITE = 2

size = 1000
Board_size = 9
Cell_Size = 50
Margin = 80
window_size = 2*Margin + Cell_Size + (Board_size-1)*Cell_Size
background = (220, 180, 140)
line_color = (0, 0, 0)
black_stone = (0, 0, 0)
white_stone = (255, 255, 255)
text_color = (0, 0, 0)
last_move = None
ai_plays_white = False
game_state = "menu"

pygame.init()
screen = pygame.display.set_mode((window_size-10, window_size-10))
pygame.display.set_caption('Go')
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

board = [[EMPTY for _ in range(Board_size)] for _ in range(Board_size)]
current_player = BLACK
previous_board = None
passes = 0
black_captures = 0
white_captures = 0
game_over = False
winner_text = "Nice work!"
last_pass_player = None
pass_display_frames = 0
ai_enabled = False 


def get_board_pos(mouse_pos):
    x, y = mouse_pos
    if Margin <= x < window_size - Margin and Margin <= y < window_size - Margin:
        col = round((x - Margin) / Cell_Size)
        row = round((y - Margin) / Cell_Size)
        return row, col
    return None, None

def get_group(board, row, col):
   
    color = board[row][col]
    if color == EMPTY:
        return set()
    visited = set()
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < Board_size and 0 <= nc < Board_size:
                if board[nr][nc] == color and (nr, nc) not in visited:
                    stack.append((nr, nc))
    return visited

def count_liberty(board, group):
    
    liberties = set()
    for r, c in group:
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < Board_size and 0 <= nc < Board_size:
                if board[nr][nc] == EMPTY:
                    liberties.add((nr, nc))
    return len(liberties)

def make_move(board, row, col, player, previous_board):

    if board[row][col] != EMPTY:
        return board, 0, False, previous_board, "Occupied"


    new_board = [row_copy[:] for row_copy in board]
    new_board[row][col] = player

    opponent = WHITE if player == BLACK else BLACK
    captured = 0


    for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < Board_size and 0 <= nc < Board_size:
            if new_board[nr][nc] == opponent:
                group = get_group(new_board, nr, nc)
                if count_liberty(new_board, group) == 0:
                   
                    for r, c in group:
                        new_board[r][c] = EMPTY
                        captured += 1

    
    placed_group = get_group(new_board, row, col)
    liberties = count_liberty(new_board, placed_group)

    
    if captured == 0 and liberties == 0:
        return board, 0, False, previous_board, "Suicide"


    if previous_board is not None and new_board == previous_board:
        return board, 0, False, previous_board, "Ko"

    global last_move
    last_move = (row, col)

    return new_board, captured, True, board, "OK"

def compute_score(board, black_captures, white_captures):
    visited = [[False for _ in range(Board_size)] for _ in range(Board_size)]
    black_score = 0
    white_score = 0


    for r in range(Board_size):
        for c in range(Board_size):
            if board[r][c] == BLACK:
                black_score += 1
            elif board[r][c] == WHITE:
                white_score += 1


    for r in range(Board_size):
        for c in range(Board_size):
            if board[r][c] == EMPTY and not visited[r][c]:
                queue = [(r, c)]
                region = []
                touches_black = False
                touches_white = False
                while queue:
                    cr, cc = queue.pop(0)
                    if (cr, cc) in region:
                        continue
                    region.append((cr, cc))
                    visited[cr][cc] = True

                    for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < Board_size and 0 <= nc < Board_size:
                            if board[nr][nc] == EMPTY and not visited[nr][nc] and (nr, nc) not in region:
                                queue.append((nr, nc))
                            elif board[nr][nc] == BLACK:
                                touches_black = True
                            elif board[nr][nc] == WHITE:
                                touches_white = True
                if touches_black and not touches_white:
                    black_score += len(region)
                elif touches_white and not touches_black:
                    white_score += len(region)

    return black_score, white_score

def draw_start_menu():
    screen.fill(background)
    title = font.render("Play Go", True, (255, 255, 255))
    screen.blit(title, (window_size//2 - 60, 40))

    # Multiplayer button
    mp_rect = pygame.Rect(window_size//2 - 120, 120, 240, 60)
    pygame.draw.rect(screen, (200, 200, 200), mp_rect)
    mp_text = font.render("Multiplayer", True, (0, 0, 0))
    screen.blit(mp_text, (mp_rect.x + 40, mp_rect.y + 15))

    # VS AI - Play as Black
    ai_black_rect = pygame.Rect(window_size//2 - 120, 200, 240, 60)
    pygame.draw.rect(screen, (200, 200, 200), ai_black_rect)
    ai_black_text = font.render("vs AI (Play Black)", True, (0, 0, 0))
    screen.blit(ai_black_text, (ai_black_rect.x + 20, ai_black_rect.y + 15))

    # VS AI - Play as White
    ai_white_rect = pygame.Rect(window_size//2 - 120, 280, 240, 60)
    pygame.draw.rect(screen, (200, 200, 200), ai_white_rect)
    ai_white_text = font.render("vs AI (Play White)", True, (0, 0, 0))
    screen.blit(ai_white_text, (ai_white_rect.x + 20, ai_white_rect.y + 15))

    # How to Play button
    howto_rect = pygame.Rect(window_size//2 - 120, 360, 240, 60)
    pygame.draw.rect(screen, (200, 200, 200), howto_rect)
    howto_text = font.render("How to Play", True, (0, 0, 0))
    screen.blit(howto_text, (howto_rect.x + 40, howto_rect.y + 15))

    return mp_rect, ai_black_rect, ai_white_rect, howto_rect
  

def draw_instructions():
    screen.fill(background)
    
    
    title = font.render("How to Play Go", True, (0, 0, 0))
    screen.blit(title, (window_size//2 - title.get_width()//2, 20))
    
    
    instructions = [
        "HOW TO PLAY:",
        "• Place stones on intersections",
        "• Surround territory to claim it",
        "• Capture stones by surrounding them",
        "• Stones need liberties (empty adjacent points)",
        "",
        "GAME RULES:",
        "• Press SPACE to pass your turn",
        "• Game ends after two consecutive passes",
        "• Winner has most territory + captures",
        "",
        "CONTROLS:",
        "• Click: Place stone",
        "• SPACE: Pass turn",
        "• AI ON/OFF: Toggle computer player",
        "",
        "Click anywhere to return"
    ]
    
    y_offset = 70
    for line in instructions:
        if line == "":
            y_offset += 10  
        else:
            text = font.render(line, True, (0, 0, 0))
            
            if y_offset + 35 < window_size - 30:
                screen.blit(text, (50, y_offset))
            y_offset += 30
    
    
    return pygame.Rect(0, 0, window_size, window_size)
    

def draw_game_over():
    screen.fill((30, 30, 30))
    msg = font.render(winner_text, True, (255, 255, 255))
    screen.blit(msg, (window_size//2 - msg.get_width()//2, 200))

    again_rect = pygame.Rect(window_size//2 - 120, 300, 240, 60)
    pygame.draw.rect(screen, (200, 200, 200), again_rect)
    again_text = font.render("Return to Menu", True, (0, 0, 0))
    screen.blit(again_text, (again_rect.x + 20, again_rect.y + 15))

    return again_rect

def draw_ai_toggle():
    toggle_rect = pygame.Rect(window_size - 180, 17, 170, 30)
    pygame.draw.rect(screen, (200, 200, 200), toggle_rect)
    
    # Determine label based on AI state
    if not ai_enabled:
        label = "AI: Off"
    elif ai_plays_as == WHITE:
        label = "AI: White"
    else:
        label = "AI: Black"
    
    text = font.render(label, True, (0, 0, 0))
    screen.blit(text, (window_size - 180, 15))
    return toggle_rect

def draw_board():
    screen.fill(background)
    toggle_rect = draw_ai_toggle()

    for i in range(Board_size):
        x = Margin + i * Cell_Size
        pygame.draw.line(screen, line_color, (x, Margin), (x, Margin + (Board_size-1)*Cell_Size), 2)
    for i in range(Board_size):
        y = Margin + i * Cell_Size
        pygame.draw.line(screen, line_color, (Margin, y), (Margin + (Board_size-1)*Cell_Size, y), 2)

    star_points = [(2,2), (2,6), (4,4), (6,2), (6,6)]
    for (x,y) in star_points:
        center = (Margin + x*Cell_Size, Margin + y*Cell_Size)
        pygame.draw.circle(screen, line_color, center, 5)


    for row in range(Board_size):
        for col in range(Board_size):
            if board[row][col] == EMPTY:
                continue
            center = (Margin + col*Cell_Size, Margin + row*Cell_Size)
            if board[row][col] == BLACK:
                pygame.draw.circle(screen, black_stone, center, Cell_Size//2 - 2)
            else:  # WHITE
                pygame.draw.circle(screen, white_stone, center, Cell_Size//2 - 2)
                pygame.draw.circle(screen, black_stone, center, Cell_Size//2 - 2, 1)

    if game_over:
        text = font.render(winner_text, True, text_color)
        screen.blit(text, (window_size//2 - 100, window_size//2))
    else:
        if current_player == BLACK:
            turn_text = f"Black's Turn, score {black_captures} to {white_captures}"
        else:
            turn_text = f"White's Turn, score {black_captures} to {white_captures}"
        text = font.render(turn_text, True, text_color)
        screen.blit(text, (10, 10))

        global last_pass_player, pass_display_frames
        if pass_display_frames > 0:
            pass_text = f"{'Black' if last_pass_player == BLACK else 'White'} passes"
            pass_surface = font.render(pass_text, True, (255, 0, 0))
            text_x = window_size//2 - pass_surface.get_width()//2
            text_y = 50
            screen.blit(pass_surface, (text_x, text_y))
            pass_display_frames -= 1

   
    if last_move is not None:
        lr, lc = last_move
        center = (Margin + lc*Cell_Size, Margin + lr*Cell_Size)
        pygame.draw.circle(screen, (0, 255, 0), center, 30, 2)

    return toggle_rect



# ==================== MAIN GAME LOOP ====================
running = True
ai_move_delay = 0
frame_count = 0

while running:
    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # ----- MENU STATE -----
        if game_state == "menu":
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Multiplayer mode
                if mp_rect.collidepoint(mouse_pos):
                    ai_enabled = False
                    # Reset game
                    board = [[EMPTY for _ in range(Board_size)] for _ in range(Board_size)]
                    current_player = BLACK
                    previous_board = None
                    passes = 0
                    black_captures = 0
                    white_captures = 0
                    game_over = False
                    last_move = None
                    game_state = "play"
                    print("Multiplayer mode selected")
                
                # VS AI - Play as Black (AI plays White)
                elif ai_black_rect.collidepoint(mouse_pos):
                    ai_enabled = True
                    ai_plays_as = WHITE  # AI plays White
                    # Reset game
                    board = [[EMPTY for _ in range(Board_size)] for _ in range(Board_size)]
                    current_player = BLACK  # Human (Black) moves first
                    previous_board = None
                    passes = 0
                    black_captures = 0
                    white_captures = 0
                    game_over = False
                    last_move = None
                    game_state = "play"
                    print("VS AI selected - You play Black, AI plays White")
                
                # VS AI - Play as White (AI plays Black)
                elif ai_white_rect.collidepoint(mouse_pos):
                    ai_enabled = True
                    ai_plays_as = BLACK  # AI plays Black
                    # Reset game
                    board = [[EMPTY for _ in range(Board_size)] for _ in range(Board_size)]
                    current_player = BLACK  # Black (AI) moves first
                    previous_board = None
                    passes = 0
                    black_captures = 0
                    white_captures = 0
                    game_over = False
                    last_move = None
                    game_state = "play"
                    print("VS AI selected - You play White, AI plays Black")
                
                # How to Play
                elif howto_rect.collidepoint(mouse_pos):
                    game_state = "instructions"

        # ----- INSTRUCTIONS STATE -----
        elif game_state == "instructions":
            if event.type == MOUSEBUTTONDOWN:
                game_state = "menu"

        # ----- PLAY STATE -----
        elif game_state == "play" and not game_over:
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if AI toggle button was clicked
                if 'toggle_rect' in locals() and toggle_rect.collidepoint(mouse_pos):
                    # Cycle through modes: Off -> White -> Black -> Off
                    if not ai_enabled:
                        ai_enabled = True
                        ai_plays_as = WHITE
                        print("AI enabled - AI plays White")
                    elif ai_plays_as == WHITE:
                        ai_plays_as = BLACK
                        print("AI now plays Black")
                    else:
                        ai_enabled = False
                        print("AI disabled - Multiplayer mode")
                    continue

                # Human move conditions:
                # - If AI is disabled (multiplayer), any player can move
                # - If AI is enabled, only move if it's NOT the AI's turn
                can_move = False
                if not ai_enabled:
                    can_move = True  # Multiplayer - both players are human
                else:
                    # AI is enabled - human moves only when it's NOT the AI's color
                    can_move = (current_player != ai_plays_as)
                
                if can_move:
                    row, col = get_board_pos(mouse_pos)
                    if row is not None and col is not None:
                        new_board, captured, valid, prev, reason = make_move(
                            board, row, col, current_player, previous_board
                        )
                        if valid:
                            board = new_board
                            if captured > 0:
                                if current_player == BLACK:
                                    black_captures += captured
                                else:
                                    white_captures += captured
                            previous_board = prev
                            passes = 0
                            print(f"Pass counter reset to 0")
                            current_player = WHITE if current_player == BLACK else BLACK
                            player_name = "Black" if current_player == BLACK else "White"
                            print(f"Human moved. Now it's {player_name}'s turn")
                        else:
                            print(f"Invalid move at {row},{col}: {reason}")

            elif event.type == KEYDOWN and event.key == K_SPACE and not game_over:
                # Human passes
                last_pass_player = current_player
                pass_display_frames = 30
                player_name = "Black" if current_player == BLACK else "White"
                print(f"Human ({player_name}) passes ({passes + 1}/2)")
                passes += 1
                
                if passes >= 2:
                    print("GAME OVER - Two passes!")
                    black_score, white_score = compute_score(board, black_captures, white_captures)
                    black_score += black_captures
                    white_score += white_captures
                    
                    if black_score > white_score:
                        winner_text = f"Black wins! {black_score} to {white_score}"
                    elif white_score > black_score:
                        winner_text = f"White wins! {white_score} to {white_score}"
                    else:
                        winner_text = "Draw!"
                    game_over = True
                    game_state = "game_over"
                else:
                    current_player = WHITE if current_player == BLACK else BLACK
                    next_player = "Black" if current_player == BLACK else "White"
                    print(f"Pass complete. Now it's {next_player}'s turn")

        # ----- GAME OVER STATE -----
        elif game_state == "game_over":
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if again_rect.collidepoint(mouse_pos):
                    game_state = "menu"

    # --- AI MOVES with MONTE CARLO TREE SEARCH ---
    if game_state == "play" and not game_over:
        # AI moves if: AI is enabled AND it's the AI's turn
        if ai_enabled and current_player == ai_plays_as:
            ai_move_delay += 1
            if ai_move_delay > 15:  # Delay for MCTS thinking time
                ai_move_delay = 0

                ai_color = "Black" if ai_plays_as == BLACK else "White"
                print(f"\n{'='*40}")
                print(f"AI ({ai_color}) TURN - Monte Carlo Thinking...")
                print(f"{'='*40}")
                empty_count = sum(row.count(EMPTY) for row in board)
                print(f"Empty spaces: {empty_count}")

                # Find all legal moves for AI
                valid_moves = []
                invalid_samples = []

                for r in range(Board_size):
                    for c in range(Board_size):
                        if board[r][c] == EMPTY:
                            _, _, valid, _, reason = make_move(board, r, c, ai_plays_as, previous_board)
                            if valid:
                                valid_moves.append((r, c))
                            else:
                                if len(invalid_samples) < 10:
                                    invalid_samples.append((r, c, reason))

                print(f"Legal moves: {len(valid_moves)}")
                if invalid_samples:
                    print("Sample illegal moves:")
                    for r, c, reason in invalid_samples:
                        print(f"  {r},{c}: {reason}")

                if valid_moves:
                    # Use MCTS for smarter move selection
                    if len(valid_moves) > 1:
                        # Determine iterations based on move count
                        if len(valid_moves) <= 3:
                            iterations = 800  # Deep search for few options
                        elif len(valid_moves) <= 8:
                            iterations = 500  # Medium search
                        else:
                            iterations = 300  # Faster for many options
                        
                        print(f"Running MCTS with {iterations} simulations...")
                        
                        # Run Monte Carlo search
                        move = monte_carlo_search(board, ai_plays_as, iterations)
                        
                        # Fallback to random if MCTS fails
                        if move is None or move not in valid_moves:
                            print(f"MCTS returned invalid move, using random selection")
                            move = valid_moves[randint(0, len(valid_moves)-1)]
                        else:
                            print(f"MCTS selected move: {move}")
                    else:
                        # Only one legal move available
                        move = valid_moves[0]
                        print(f"Only one legal move: {move}")
                    
                    # Execute the chosen move
                    new_board, captured, valid, prev, reason = make_move(
                        board, move[0], move[1], ai_plays_as, previous_board
                    )
                    
                    if valid:
                        board = new_board
                        if captured > 0:
                            if ai_plays_as == BLACK:
                                black_captures += captured
                            else:
                                white_captures += captured
                            print(f"AI captured {captured} stones!")
                        previous_board = prev
                        passes = 0
                        print(f"Pass counter reset to 0")
                        current_player = WHITE if current_player == BLACK else BLACK
                        next_player = "Black" if current_player == BLACK else "White"
                        print(f"AI moved. Now it's {next_player}'s turn")
                    else:
                        # This shouldn't happen if move was in valid_moves
                        print(f"ERROR: Selected move {move} became invalid: {reason}")
                        # Fallback to random move
                        move = valid_moves[randint(0, len(valid_moves)-1)]
                        new_board, captured, valid, prev, reason = make_move(
                            board, move[0], move[1], ai_plays_as, previous_board
                        )
                        if valid:
                            board = new_board
                            if captured > 0:
                                if ai_plays_as == BLACK:
                                    black_captures += captured
                                else:
                                    white_captures += captured
                            previous_board = prev
                            passes = 0
                            current_player = WHITE if current_player == BLACK else BLACK
                else:
                    # No legal moves -> pass
                    print(f"AI has NO legal moves. Passing ({passes + 1}/2)")
                    last_pass_player = ai_plays_as
                    pass_display_frames = 30
                    passes += 1
                    
                    if passes >= 2:
                        print("GAME OVER - Two consecutive passes!")
                        black_score, white_score = compute_score(board, black_captures, white_captures)
                        black_score += black_captures
                        white_score += white_captures
                        
                        if black_score > white_score:
                            winner_text = f"Black wins! {black_score} to {white_score}"
                        elif white_score > black_score:
                            winner_text = f"White wins! {white_score} to {white_score}"
                        else:
                            winner_text = "Draw!"
                        game_over = True
                        game_state = "game_over"
                    else:
                        current_player = WHITE if current_player == BLACK else BLACK
                        next_player = "Black" if current_player == BLACK else "White"
                        print(f"AI passed. Now it's {next_player}'s turn (pass count: {passes})")

    # --- DRAWING ---
    if game_state == "menu":
        mp_rect, ai_black_rect, ai_white_rect, howto_rect = draw_start_menu()
    
    elif game_state == "instructions":
        howto_rect = draw_instructions()
    
    elif game_state == "play":
        # Draw AI thinking indicator during MCTS
        if ai_enabled and current_player == ai_plays_as and ai_move_delay > 0:
            thinking_text = font.render("AI thinking...", True, (100, 100, 100))
            screen.blit(thinking_text, (window_size - 250, 80))
        
        toggle_rect = draw_board()
        if game_over:
            again_rect = draw_game_over()
    
    elif game_state == "game_over":
        again_rect = draw_game_over()

    pygame.display.flip()
    frame_count += 1
    clock.tick(30)

print("Game ended")
pygame.quit()
sys.exit()