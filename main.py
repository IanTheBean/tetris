# imports
import sys
import pygame
from PIL import Image
import random
from pygame.locals import *


# constants
GAME_WIDTH = 300
GAME_HEIGHT = 600

ROWS = 20
COLUMNS = 10

UPDATE_TIME = 20

SPAWN = (5, 1)

SCORE = 0

# setup
pygame.init()

fps = 60
fps_counter = 0
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("tetris")


def check_cell(_x, _y, _grid):
    if _x > _grid.columns-1 or _x < 0 or _y < 0 or _y > _grid.rows or _grid.grid[_y, _x] != (0, 0, 0):
        return False
    return True


# classes
class Block:
    def __init__(self, _screen, _spawn):
        self.blocks = [[]]
        self.screen = _screen

        self.spawn = _spawn
        self.rotation = 0

        self.x = 0
        self.y = 0

        self.color = (0, 0, 0)

        self.respawn()


    def respawn(self):
        i_piece = [[(1, 0), (0, 0), (-1, 0), (-2, 0)], [(0, 0), (0, -1), (0, 1), (0, 2)]]
        j_piece = [[(-1, -1), (-1, 0), (1, 0), (0, 0)], [(0, 0), (0, -1), (1, -1), (0, 1)], [(0, 0), (-1, 0), (1, 1), (1, 0)], [(0, 0), (0, 1), (0, -1), (-1, 1)]]
        l_piece = [[(1, -1), (-1, 0), (1, 0), (0, 0)], [(0, 0), (0, -1), (1, 1), (0, 1)], [(0, 0), (-1, 0), (-1, 1), (1, 0)], [(0, 0), (0, 1), (0, -1), (-1, -1)]]
        o_piece = [[(0, 0), (-1, 0), (-1, -1), (0, -1)]]
        s_piece = [[(0, 0), (-1, 0), (0, -1), (1, -1)], [(0, 0), (0, -1), (1, 1), (1, 0)]]
        t_piece = [[(0, 0), (-1, 0), (1, 0), (0, -1)], [(0, 0), (0, 1), (1, 0), (0, -1)], [(0, 0), (0, 1), (1, 0), (-1, 0)], [(0, 0), (0, 1), (0, -1), (-1, 0)]]
        z_piece = [[(0, 0), (0, -1), (-1, -1), (1, 0)], [(0, 0), (0, 1), (1, -1), (1, 0)]]

        pieces = [i_piece, j_piece, l_piece, o_piece, s_piece, t_piece, z_piece]

        blue = (58, 126, 222)
        orange = (254, 181, 83)
        yellow = (255, 255, 128)
        green = (106, 185, 49)
        pink = (208, 100, 199)
        red = (228, 90, 90)
        purple = (188, 99, 226)

        colors = [blue, orange, yellow, green, pink, red, purple]

        self.rotation = 0
        self.x = self.spawn[0]
        self.y = self.spawn[1]
        self.color = colors[random.randint(0, len(colors) - 1)]
        self.blocks = pieces[random.randint(0, len(pieces) - 1)]

    def rotate(self, _grid):

        new_rotation = 0
        can_rotate = True
        if self.rotation == len(self.blocks) - 1:
            new_rotation = 0
        else:
            new_rotation = self.rotation + 1
        for _block in self.blocks[new_rotation]:
            if not check_cell(self.x + _block[0], self.y + _block[1], _grid):
                can_rotate = False
        if can_rotate:
            self.rotation = new_rotation
            self.check_col(_grid)

    def draw(self):
        for _block in self.blocks[self.rotation]:
            pygame.draw.rect(self.screen, self.color, Rect((_block[0] * 30) + (self.x * 30), (_block[1] * 30) + (self.y * 30), 30, 30))

    def drop(self):
        self.y += 1

    def move(self, _dir, _grid):
        can_move = True
        for _block in self.blocks[self.rotation]:
            new_x = self.x + _block[0] + _dir
            new_y = self.y + _block[1]
            if not check_cell(new_x, new_y, _grid):
                can_move = False
        if can_move:
            self.x += _dir
            self.check_col(_grid)

    def check_col(self, _grid):
        for _block in self.blocks[self.rotation]:
            y = self.y + _block[1]
            x = self.x + _block[0]
            if y == _grid.rows - 1 or _grid.grid[y + 1, x] != (0, 0, 0):
                _grid.add(self)
                self.respawn()


class Grid:
    def __init__(self, _screen, _rows, _columns, _width, _height):
        self.screen = _screen

        self.rows = _rows
        self.columns = _columns

        self.width = _width
        self.height = _height

        self.grid = Image.new('RGB', (_rows, _columns), (0, 0, 0)).load()

    # draws the grid
    def draw_grid(self):
        # draw the horizontal lines
        for i in range(1, self.rows):
            row_pos = self.height / self.rows
            pygame.draw.line(self.screen, (142, 154, 166), (0, i * row_pos), (self.width, i * row_pos), 1)

        # draw the vertical lines
        for i in range(1, self.columns):
            row_pos = self.width / self.columns
            pygame.draw.line(self.screen, (142, 154, 166), (i * row_pos, 0), (i * row_pos, self.height), 1)

        row_num = 0
        for y in range(self.rows):
            for x in range(self.columns):
                if self.grid[y, x] != (0, 0, 0):
                    pygame.draw.rect(self.screen, self.grid[y, x], Rect(x * 30, y * 30, 30, 30))

    def add(self, _block):
        for __block in _block.blocks[_block.rotation]:
            x = _block.x + __block[0]
            y = _block.y + __block[1]
            self.grid[y, x] = _block.color

    def clear_line(self):
        for y in range(self.rows):
            row = 0
            for x in range(self.columns):
                if self.grid[y, x] != (0, 0, 0):
                    row += 1
            if row == 10:
                for x in range(self.columns):
                    self.grid[y, x] = (0, 0, 0)
                    row = 0
                for i in range(y-1):
                    for x in range(self.columns):
                        self.grid[(y-1) - i + 1, x] = self.grid[(y-1) - i, x]


grid = Grid(screen, ROWS, COLUMNS, GAME_WIDTH, GAME_HEIGHT)
block = Block(screen, SPAWN)
# game loop.
while True:
    # draw the background
    screen.fill((113, 125, 137))

    # update the blocks
    fps_counter += 1
    grid.clear_line()
    if fps_counter >= UPDATE_TIME:
        block.drop()
        block.check_col(grid)
        fps_counter = 0

    # check for input
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                block.move(-1, grid)
            if event.key == pygame.K_d:
                block.move(1, grid)
            if event.key == pygame.K_SPACE:
                block.rotate(grid)

    # draw
    grid.draw_grid()
    block.draw()

    pygame.display.flip()
    fpsClock.tick(fps)

