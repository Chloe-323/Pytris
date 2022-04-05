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
bottom_rects = []
bottom_rects_draw = []


#SO let me work through this in english first:
#The standard way to rotate blocks is to have each block be housed in a 4x4 grid and have them move around in that grid.
#Every block is therefore 16 rects that are either 1 or 0, and only the ones that have a 1 are drawn.
class Block:
    valid = True
    rects = [[None for i in range(4)] for j in range(4)]
    coords = [None]*4
    pivot = (1, 1)
    color = (255, 255, 255)
    def __init__(self, blocktype):
        for i in range(4):
            for j in range(4):
                self.rects[i][j] = pygame.Rect(i * block_size, j * block_size, block_size, block_size)
        blocktype = 1
        if blocktype == 0: #Z
            self.color = (255, 0, 0)
            self.coords = [(-1, -1), (0, 0), (-1, 0), (0, 1)]
            return
        elif blocktype == 1: #T
            self.color = (255, 0, 255)
            self.coords = [(0, -1), (0, 0), (-1, 0), (1, 0)]
            return
        elif blocktype == 2: #S
            self.color = (0, 255, 0)
            self.coords = [(0, -1), (0, 0), (-1, 0), (-1, 1)]
            return
        elif blocktype == 3: #I
            self.color = (120, 120, 255)
            self.coords = [(0, -1), (0, 0), (0, 1), (0, 2)]
            return
        elif blocktype == 4: #L
            self.color = (255, 120, 0)
            self.coords = [(-1, -1), (-1, 0), (-1, 1), (0, 1)]
            return
        elif blocktype == 5: #J
            self.color = (0, 0, 255)
            self.coords = [(0, -1), (0, 0), (0, 1), (-1, 1)]
            return
        elif blocktype == 6: #O
            self.color = (255, 255, 0)
            self.coords = [(-1, -1), (-1, 0), (0, -1), (0, 0)]
            return
        else:
            self.valid = False

    def _resolve_rect(self, coords):
        return self.rects[coords[0] + self.pivot[0]][coords[1] + self.pivot[1]]

    def move(self, x, y):
        if not self.valid:
            return
        for i in self.rects:
            for j in i:
                j.move_ip(x, y)
        if self._is_offscreen():
            for i in self.rects:
                for j in i:
                    j.move_ip(-x, -y)
        return

    def drop(self):
        if not self.valid:
            return
        for i in self.rects:
            for j in i:
                j.move_ip(0, block_size)
        if self._is_bottom():
            for i in self.rects:
                for j in i:
                    j.move_ip(0, -block_size)
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
        for i in self.coords:
            pygame.draw.rect(screen, self.color, self._resolve_rect(i))

        self.draw_ghost()

    def draw_ghost(self):
        realself = copy.deepcopy(self.rects)
        while not self._is_bottom():
            for i in self.rects:
                for j in i:
                    j.move_ip(0, block_size)
        for i in self.rects:
            for j in i:
                j.move_ip(0, -block_size)
        for i in self.coords:
            pygame.draw.rect(screen, (120, 120, 120), self._resolve_rect(i), 2)
        self.rects = realself

    def _is_bottom(self):
        for i in self.coords:
            if self._resolve_rect(i).collidelistall(bottom_rects):
                return True
            if self._resolve_rect(i).bottom > height:
                return True
        return False

    def _is_offscreen(self):
        for i in self.coords:
            if self._resolve_rect(i).left < 0 or self._resolve_rect(i).right > width:
                return True
        return False

    def _delete_self(self):
        self.valid = False
        return
    def __del__(self):
        for i in self.coords:
            bottom_rects.append(self._resolve_rect(i))
            bottom_rects_draw.append((self.color, self._resolve_rect(i)))
            self.valid = False
        return


def is_row_full(row):
    #assumptions:
    #grid_size[0] rects in full row
    #rects cannot overlap
    found_rects = 0
    for i in bottom_rects:
        if i.top == row * block_size: #in current row
            found_rects += 1
    if found_rects == grid_size[0]:
        return True
    elif found_rects < grid_size[0]:
        return False
    elif found_rects > grid_size[0]:
        print("This should never happen!!")
        raise OverflowError

def sweep_rows():
    for row in range(grid_size[1]):
        if is_row_full(row):
            drop_one = []
            idx_offset = 0
            for i in range(len(bottom_rects)):
                print(bottom_rects[i - idx_offset].top, "; ", row * block_size)
                if bottom_rects[i - idx_offset].top == row * block_size:
                    bottom_rects.pop(i - idx_offset)
                    bottom_rects_draw.pop(i - idx_offset)
                    idx_offset += 1
                elif bottom_rects[i - idx_offset].top < (row * block_size - block_size):
                    drop_one.append(i - idx_offset)
            for i in drop_one:
                bottom_rects[i].move_ip(0, block_size)
                bottom_rects_draw[i][1].move_ip(0, block_size)
                bottom_rects_draw[i] = ((40, 0, 0), bottom_rects_draw[i][1])

def lose():
    print("You lost!")
    exit(0)

def main():
#    avb_blocks = gen_avb_blocks()
    cur_block = Block(random.randint(0, 6))
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
                    cur_block.move(-block_size, 0)
                if keypress == pygame.K_d or keypress == pygame.K_RIGHT:
                    cur_block.move(block_size, 0)
                if keypress == pygame.K_w or keypress == pygame.K_UP:
                    cur_block.rotate()
                if keypress == pygame.K_s or keypress == pygame.K_DOWN:
                    cur_block.drop_to_bottom()
            

        cur_block.drop()
        sweep_rows()
        if not cur_block.valid:
            del cur_block
            cur_block = Block(random.randint(0, 6))
            if cur_block._is_bottom():
                lose()
        #new b
#       if(cur_block == None):
#           cur_block = copy.deepcopy(random.choice(avb_blocks))
#           move_block(cur_block, width / 2, 0)
#       else:
#           drop_block(cur_block)

#       if is_bottom(cur_block):
#           move_block(cur_block, 0, -speed)
#           bottom_rects.extend(cur_block[1])
#           for i in cur_block[1]:
#               bottom_rects_draw.append((cur_block[0], i))
#           cur_block = None
        screen.fill(black)

#       if(cur_block != None):
#           for i in cur_block[1]:
#               pygame.draw.rect(screen, cur_block[0], i)

        cur_block.draw()
        for i in bottom_rects_draw:
            pygame.draw.rect(screen, i[0], i[1])
        pygame.display.flip()

main()
