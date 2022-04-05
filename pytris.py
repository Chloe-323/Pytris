import sys
import random
import copy
import pygame
import math

pygame.init()

#global variables (OOH SCARY)
speed = 60
black = 0, 0, 0
fps = 5
block_size = 30
grid_size = (10, 22)
size = width, height = block_size * grid_size[0], block_size * grid_size[1] 
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

cur_block = None
bottom_rects = [[None for i in range(grid_size[1])] for j in range(grid_size[0])]

class Tetromino:
    valid = True
    rects = [[None for i in range(4)] for j in range(4)]
    coords = [None]*4
    pivot = (1, 1)
    color = (255, 255, 255)
    x, y = 1, 1
    def __init__(self, blocktype):
        for i in range(4):
            for j in range(4):
                self.rects[i][j] = pygame.Rect(i * block_size, j * block_size, block_size, block_size)
        if blocktype == 0: #Z
            self.color = (255, 0, 0)
            self.coords = [(-1, -1), (0, 0), (-1, 0), (0, 1)]
        elif blocktype == 1: #T
            self.color = (255, 0, 255)
            self.coords = [(0, -1), (0, 0), (-1, 0), (1, 0)]
        elif blocktype == 2: #S
            self.color = (0, 255, 0)
            self.coords = [(0, -1), (0, 0), (-1, 0), (-1, 1)]
        elif blocktype == 3: #I
            self.color = (120, 120, 255)
            self.coords = [(0, -1), (0, 0), (0, 1), (0, 2)]
        elif blocktype == 4: #L
            self.color = (255, 120, 0)
            self.coords = [(-1, -1), (-1, 0), (-1, 1), (0, 1)]
        elif blocktype == 5: #J
            self.color = (0, 0, 255)
            self.coords = [(0, -1), (0, 0), (0, 1), (-1, 1)]
        elif blocktype == 6: #O
            self.color = (255, 255, 0)
            self.coords = [(-1, -1), (-1, 0), (0, -1), (0, 0)]
        else:
            self.valid = False
        self.move(4, 0)

    def _resolve_rect(self, coords):
        return self.rects[coords[0] + self.pivot[0]][coords[1] + self.pivot[1]]

    def _absolute_coords(self):
        return [(i[0] + self.x, i[1] + self.y) for i in self.coords]

    def move(self, x, y):
        if not self.valid:
            return
        for i in self.rects:
            for j in i:
                j.move_ip(x * block_size, y * block_size)
        self.x += x
        self.y += y
        if self._is_offscreen():
            for i in self.rects:
                for j in i:
                    j.move_ip(-x * block_size, -y * block_size)
            self.x -= x
            self.y -= y
        return

    def drop(self):
        if not self.valid:
            return
        for i in self.rects:
            for j in i:
                j.move_ip(0, block_size)
        self.y += 1
        if self._is_bottom():
            for i in self.rects:
                for j in i:
                    j.move_ip(0, -block_size)
            self.y -= 1
            self._delete_self()
        return

    def rotate(self):
        if not self.valid:
            return
        old_coords = self.coords
        for i in range(len(self.coords)):
            self.coords[i] = (-self.coords[i][1], self.coords[i][0])
        if not self._is_bottom() and not self._is_offscreen():
            self.coords = old_coords
        return

    def drop_to_bottom(self):
        while self.valid:
            self.drop()
        return

    def draw(self):
        if not self.valid:
            return
        for i in self._absolute_coords():
            pygame.draw.rect(screen, self.color, pygame.Rect(i[0] * block_size, i[1] * block_size, block_size, block_size))
        for i in self.coords:
            pygame.draw.rect(screen, (120, 120, 120), self._resolve_rect(i), 2)
#            pygame.draw.rect(screen, self.color, pygame.Rect((self.x + i[0]) * block_size, (self.y + i[1]) * block_size, block_size, block_size))

        self.draw_ghost()

    def draw_ghost(self):
        realself = copy.deepcopy(self.rects)
        realy = self.y
        while not self._is_bottom():
            for i in self.rects:
                for j in i:
                    j.move_ip(0, block_size)
            self.y += 1
        for i in self.rects:
            for j in i:
                j.move_ip(0, -block_size)
        for i in self.coords:
            pygame.draw.rect(screen, (120, 120, 120), self._resolve_rect(i), 2)
        self.rects = realself
        self.y = realy

    def _is_bottom(self):
        for i in self._absolute_coords():
            if i[1] >= grid_size[1]:
                return True
            if bottom_rects[i[0]][i[1]] is not None:
                return True
        return False

    def _is_offscreen(self):
        for i in self._absolute_coords():
            if i[0] < 0 or i[0] >= grid_size[0]:
                return True
        return False

    def _delete_self(self):
        self.valid = False
        return
    def __del__(self):
        for i in self._absolute_coords():
            bottom_rects[i[0]][i[1]] = self.color
            self.valid = False
        return


def is_row_full(row):
    #assumptions:
    #grid_size[0] rects in full row
    #rects cannot overlap
    for i in range(grid_size[0]):
        if bottom_rects[i][row] == None:
            return False
    return True

def sweep_rows():
    rows_cleared = 0
    for row in range(grid_size[1] - 1, -1, -1):
        if rows_cleared != 0:
            print("shifting row", row, "down!")
            for i in range(grid_size[0]):
                bottom_rects[i][row + rows_cleared] = bottom_rects[i][row]
                bottom_rects[i][row] = None
        if is_row_full(row):
            print("row", row, "full!")
            for i in range(grid_size[0]):
                bottom_rects[i][row] = None
            rows_cleared += 1



def lose():
    print("You lost!")
    exit(0)

def main():
#    avb_blocks = gen_avb_blocks()
    cur_block = Tetromino(random.randint(0, 6))
    while 1:
        #framerate cap
        clock.tick(fps)

        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keypress = event.__dict__["key"]
                if keypress == pygame.K_a or keypress == pygame.K_LEFT:
                    cur_block.move(-1, 0)
                if keypress == pygame.K_d or keypress == pygame.K_RIGHT:
                    cur_block.move(1, 0)
                if keypress == pygame.K_w or keypress == pygame.K_UP:
                    cur_block.rotate()
                if keypress == pygame.K_s or keypress == pygame.K_DOWN:
                    cur_block.drop_to_bottom()
            

        cur_block.drop()
        sweep_rows()
        if not cur_block.valid:
            del cur_block
            cur_block = Tetromino(random.randint(0, 6))

        screen.fill(black)

        cur_block.draw()
        for i in range(len(bottom_rects)):
            for j in range(len(bottom_rects[i])):
                if bottom_rects[i][j] is not None:
                    pygame.draw.rect(screen, bottom_rects[i][j], 
                            pygame.Rect(i * block_size, j * block_size, block_size, block_size))
        pygame.display.flip()

main()
