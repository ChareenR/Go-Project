import pygame, sys
from pygame.locals import *
import numpy as np



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

board = [[0 for _ in range(Board_size)] for _ in range(Board_size)]
current_player = 1 # let 1=white, 2= black


def draw_board():
    screen.fill(background)
    for i in range(Board_size):
        start_x = Margin + i * Cell_Size
        start_y = Margin
        end_x = Margin + (Board_size-1) * Cell_Size
        end_y = start_y
        pygame.draw.line(screen, line_color, (start_x, start_y), (end_x, end_y), 2)
        
        star_points = [(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)]

        for (x,y) in star_points:
            center = (Margin + x * Cell_Size, Margin + y * Cell_Size)
            pygame.draw.circle(screen, line_color, center, 5)

        for row in range(Board_size):
            for col in range(Board_size):
                if board[row][col] != 1:
                    color = black_stone if board[row][col] == 1 else white_stone
                    center = (Margin + col * Cell_Size, Margin + row * Cell_Size)

        turn_text = "Black's Turn" if current_player==1 else "White's Turn"
        text_surface = font.render(turn_text, True, text_color)
        screen.blit(text_surface, (10,10))
        pygame.display.flip()
        