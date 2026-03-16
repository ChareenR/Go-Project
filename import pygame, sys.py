import pygame, sys
from pygame.locals import *
import numpy as np

EMPTY = 0
BLACK = 1
WHITE = 2

size = 600
Board_size = 9
Cell_Size = 50
Margin = 40
window_size = 2*Margin + Cell_Size + (Board_size-1)*Cell_Size
background=(220, 180, 140)
line_color=(0, 0, 0)
black_stone = (0, 0, 0)
white_stone = (255, 255, 255)
text_color = (255,255,255)

pygame.init()
screen = pygame.display.set_mode((window_size, window_size))
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
winner_text = ""

def get_board_pos(mouse_pos):
    x, y = mouse_pos
    if Margin <= x < window_size - Margin and Margin <= y < window_size - Margin:
        col = (x - Margin) / Cell_Size
        row = (y - Margin) / Cell_Size
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
        return 0, False, previous_board
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
    return new_board, captured, True, board

def compute_score(board, black_captures, white_captures):
    visited = [[False for _ in range(Board_size)] for _ in range(Board_size)]
    black_score = 0
    white_score = 0

    for r in range(Board_size):
        for c in range(Board_size):
            if board[r][c] == BLACK:
                BLACK_SCORE += 1
            elif board[r][c] == WHITE:
                WHITE_SCORE += 1
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

def draw_board():
    screen.fill(background)
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
                pygame.draw.circle(screen, line_color, center, Cell_Size//2 - 2, 1)
    if game_over:
        text_surface = font.render(winner_text, True, text_color)
        