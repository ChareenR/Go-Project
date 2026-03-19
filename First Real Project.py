import pygame, sys
from pygame.locals import *
import numpy as np
from random import randint

EMPTY = 0
BLACK = 1
WHITE = 2

size = 600
Board_size = 9
Cell_Size = 50
Margin = 50
window_size = 2*Margin + Cell_Size + (Board_size-1)*Cell_Size
background=(220, 180, 140)
line_color=(0, 0, 0)
black_stone = (0, 0, 0)
white_stone = (255, 255, 255)
text_color = (0,0,0)
last_move = None
ai_plays_white = False


pygame.init()
screen = pygame.display.set_mode((window_size-10, window_size-10))
pygame.display.set_caption('Go Version 1.0')
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

def get_board_pos(mouse_pos):
    x, y = mouse_pos
    if Margin <= x < window_size - Margin and Margin <= y < window_size - Margin:
        col = round((x - Margin) / Cell_Size)
        row = round((y - Margin) / Cell_Size)
        return row, col
    return None, None

def get_group(board, row, col,):
    color = board[row][col]
    if color == EMPTY:
        return set()
    visted = set()
    stack = [(row, col)]
    while stack:
        r,c = stack.pop()
        if (r,c) in visted:
            continue
        visted.add((r,c))
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < Board_size and 0 <= nc < Board_size:
                if board[nr][nc] == color and (nr,nc) not in visted:
                    stack.append((nr,nc))
    return visted

def count_liberty(board, group):
    liberty = set()
    for r, c in group:
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < Board_size and 0 <= nc < Board_size:
                if board[nr][nc] == EMPTY:
                    liberty.add((nr, nc))
    return len(liberty)

def make_move(board, row, col, player, previous_board):
    if board[row][col] != EMPTY:
        return board, 0, False, previous_board
    new_board = [row_copy[:] for row_copy in board]
    new_board[row][col] = player
    captured = 0
    opponent = WHITE if player == BLACK else BLACK
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < Board_size and 0 <= nc < Board_size:
            if new_board[nr][nc] == opponent:
                group = get_group(new_board, nr, nc)
                if count_liberty(new_board, group) == 0:
                    captured += len(group)
                    for r,c in group:
                        new_board[r][c] = EMPTY
                        captured += 1
    placed_group = get_group(new_board, row, col)
    if count_liberty(new_board, placed_group) == 0:
        new_board[row][col] = EMPTY
        return board, 0, False, previous_board
    if previous_board is not None and new_board == previous_board:
        return board, 0, False, previous_board
    
    global last_move
    last_move = (row, col)
    
    return new_board, captured, True, board

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
                    if (cr,cc) in region:
                        continue
                    region.append((cr, cc))
                    visited[cr][cc] = True

                    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < Board_size and 0 <= nc < Board_size:
                            if board[nr][nc] is not EMPTY and not visited[nr][nc] and (nr, nc) not in region:
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



def draw_ai_toggle():
    toggle_rect = pygame.Rect(window_size - 180, 17, 170, 30)
    pygame.draw.rect(screen, (200, 200, 200), toggle_rect)
    label = "AI ON" if ai_plays_white else "AI Plays Black"
    text = font.render(label, True, (0, 0, 0))
    screen.blit(text, (window_size - 180, 15))
    return toggle_rect


def handle_ai_move():
    global board, current_player, previous_board, white_captures
    valid_moves = []
    for r in range(Board_size):
        for c in range(Board_size):
            if board[r][c] == EMPTY:
                new_board, captured, valid, _ = make_move(board, r, c, WHITE, previous_board)
                if valid:
                    valid_moves.append((r,c))
    if valid_moves:
        move = valid_moves[randint(0, len(valid_moves)-1)]
        new_board, captured, valid, prev = make_move(board, move[0], move[1], WHITE, previous_board)
        if valid:
            board = new_board
            if captured > 0:
                white_captures += captured
            previous_board = prev
            current_player = BLACK



def draw_board():
    screen.fill(background)
    toggle_rect = draw_ai_toggle()
    for i in range(Board_size):
        x = Margin + i * Cell_Size
        pygame.draw.line(screen, line_color, (x, Margin), (x, Margin + (Board_size-1)* Cell_Size), 2)
    for i in range(Board_size):
        y = Margin + i * Cell_Size
        pygame.draw.line(screen, line_color, (Margin, y), (Margin + (Board_size-1) * Cell_Size, y), 2)
    star_points = [(2, 2), (2, 6), (4,4), (6, 2), (6, 6)]
    for (x,y) in star_points:
        center = (Margin + x * Cell_Size, Margin + y * Cell_Size)
        pygame.draw.circle(screen, line_color, center, 5)
    
    for row in range(Board_size):
        for col in range(Board_size):
            if board[row][col] == EMPTY:
                continue
            center = (Margin + col * Cell_Size, Margin + row * Cell_Size)
            if board[row][col] == BLACK:
                pygame.draw.circle(screen, black_stone, center, Cell_Size//2 - 2)
            elif board[row][col] == WHITE:
                pygame.draw.circle(screen, white_stone, center, Cell_Size//2 - 2)

                pygame.draw.circle(screen, black_stone, center, Cell_Size//2 - 2, 1)

    if game_over:
        text = font.render(winner_text, True, text_color)
        screen.blit(text, (window_size//2 - 100, window_size//2 ))
    else:
        if current_player == BLACK:
            turn_text =f"Black's Turn, score {black_captures} to {white_captures}"
        else:
            turn_text =f"White's Turn, score {black_captures} to {white_captures}"
        text = font.render(turn_text, True, text_color)
        screen.blit(text, (10, 10))

    if last_move is not None:
        lr, lc = last_move
        center = (Margin + lc * Cell_Size, Margin + lr * Cell_Size)
        pygame.draw.circle(screen, (0, 255, 0), center, 30,2)
    return toggle_rect

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == MOUSEBUTTONDOWN and not game_over:
            mouse_pos = pygame.mouse.get_pos()
            toggle_rect = draw_board()
            if toggle_rect.collidepoint(mouse_pos):
                ai_plays_white = not ai_plays_white
                continue
            row, col = get_board_pos(mouse_pos)
            if row is not None and col is not None:
                new_board, captured, valid, previous_board = make_move(board, row, col, current_player, previous_board)
                if valid:
                    board = new_board
                    if captured > 0:
                        if current_player == BLACK:
                            black_captures += captured
                        else:
                            white_captures += captured
                    passes = 0
                    current_player = WHITE if current_player == BLACK else BLACK
                else:
                    print("Invalid move")
            

        elif event.type == KEYDOWN and event.key == K_SPACE and not game_over:
            passes += 1
            if passes >= 2:
                black_score, white_score = compute_score(board, black_captures, white_captures)
                if black_score > white_score:
                    winner_text = f"Black wins! {black_score} to {white_score}"
                elif white_score > black_score:
                    winner_text = f"White wins! {white_score} to {black_score}"
                else:
                    winner_text = "I declare this to be a draw!"
                game_over = True
            else:
                current_player = WHITE if current_player == BLACK else BLACK

    draw_board()
    pygame.display.flip()
    if not game_over and current_player == WHITE and ai_plays_white:
        handle_ai_move()
    clock.tick(10)

