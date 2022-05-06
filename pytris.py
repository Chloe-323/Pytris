import sys
import random
import copy
import math
import json
from collections import deque
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys, tty

pygame.init()
print("Welcome to Pytris! A simple Tetris implementation written in Python using the Pygame engine")
print("Written by Chloe323 (https://github.com/Chloe-323)")
print("")
print("Controls:")
print("⬅ or A\tMove left")
print("➡ or D\tMove right")
print("⬆ or W\tRotate")
print("⬇ or S\tDrop")
print("SHIFT\tHold/Swap held")

#global variables (OOH SCARY)
speed = 60
black = 0, 0, 0
fps = 60
block_size = 45
grid_size = (10, 22)
size = width, height = block_size * grid_size[0] + 400, block_size * grid_size[1] 
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 25)
font_big = pygame.font.Font(None, 35)


class Tetromino:
    valid = True
    rects = [[None for i in range(4)] for j in range(4)]
    coords = [None]*4
    pivot = (1, 1)
    color = (255, 255, 255)
    blocktype = -1
    x, y = 1, 1
    def __init__(self, br, blocktype = -1):
        self.bottom_rects = br
        for i in range(4):
            for j in range(4):
                self.rects[i][j] = pygame.Rect(i * block_size, j * block_size, block_size, block_size)
                self.rects[i][j].move_ip(3 * block_size, 0)
        if blocktype == -1:
            blocktype = random.randint(0, 6)
        self.blocktype = blocktype
        if blocktype == 0: #Z
            self.color = (255, 0, 0)
            self.coords = [(0, -1), (0, 0), (-1, 0), (-1, 1)]
        elif blocktype == 1: #T
            self.color = (255, 0, 255)
            self.coords = [(0, -1), (0, 0), (-1, 0), (1, 0)]
        elif blocktype == 2: #S
            self.color = (0, 255, 0)
            self.coords = [(-1, -1), (0, 0), (-1, 0), (0, 1)]
        elif blocktype == 3: #I
            self.pivot = (1.5, 1.5)
            self.x, self.y = 1.5, 1.5
            self.color = (120, 120, 255)
            self.coords = [(-0.5, -1.5), (-0.5, -0.5), (-0.5, 0.5), (-0.5, 1.5)]
        elif blocktype == 4: #L
            self.color = (255, 120, 0)
            self.coords = [(-1, -1), (-1, 0), (-1, 1), (0, 1)]
        elif blocktype == 5: #J
            self.color = (0, 0, 255)
            self.coords = [(0, -1), (0, 0), (0, 1), (-1, 1)]
        elif blocktype == 6: #O
            self.pivot = (0.5, 0.5)
            self.x, self.y = 0.5, 0.5
            self.color = (255, 255, 0)
            self.coords = [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]
        else:
            self.valid = False
        self.x += 3
#        self.move(4, 0)

    def _resolve_rect(self, coords):
        return self.rects[int(coords[0] + self.pivot[0])][int(coords[1] + self.pivot[1])]

    def _absolute_coords(self):
        return [(int(i[0] + self.x), int(i[1] + self.y)) for i in self.coords]

    def move(self, x, y):
        if not self.valid:
            return
        for i in self.rects:
            for j in i:
                j.move_ip(x * block_size, y * block_size)
        self.x += x
        self.y += y
        if self._is_offscreen() or self._is_bottom():
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
        if self._is_offscreen() or self._is_bottom():
            for i in self.rects:
                for j in i:
                    j.move_ip(0, -block_size)
            self.y -= 1
            self._delete_self()
        return

    def rotate(self):
        if not self.valid:
            return
        old_coords = copy.deepcopy(self.coords)
        for i in range(len(self.coords)):
            self.coords[i] = (-self.coords[i][1], self.coords[i][0])
        if (self._is_offscreen()) or (self._is_bottom()):
            self.coords = old_coords
        return

    def drop_to_bottom(self):
        count = 0
        while self.valid:
            self.drop()
            count += 1
        return count

    def draw(self, screen, ghost = True):
        if not self.valid:
            return
        for i in self.coords:
            pygame.draw.rect(screen, self.color, self._resolve_rect(i))
        if ghost:
            self.draw_ghost(screen)

    def draw_ghost(self, screen):
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
#       if self._is_offscreen():
#           return True
        if self.bottom_rects == None:
            return False
        for i in self._absolute_coords():
            if i[1] >= grid_size[1]:
                return True
            if self.bottom_rects[i[0]][i[1]] is not None:
                return True
        return False

    def _is_offscreen(self):
        if self.bottom_rects == None:
            return False
        for i in self._absolute_coords():
            if i[0] < 0 or i[0] >= grid_size[0]:
                return True
        return False

    def _delete_self(self):
        self.valid = False
        for i in self._absolute_coords():
            self.bottom_rects[i[0]][i[1]] = self.color
        return
    def __del__(self):
        return


def is_row_full(row, bottom_rects):
    for i in range(grid_size[0]):
        if bottom_rects[i][row] == None:
            return False
    return True

def sweep_rows(bottom_rects):
    total_rows_cleared = 0
    for d in range(4):
        rows_cleared = 0
        for row in range(grid_size[1] - 1, -1, -1):
            if rows_cleared != 0:
                for i in range(grid_size[0]):
                    bottom_rects[i][row + rows_cleared] = bottom_rects[i][row]
                    bottom_rects[i][row] = None
            if is_row_full(row, bottom_rects):
                for i in range(grid_size[0]):
                    bottom_rects[i][row] = None
                rows_cleared += 1
        total_rows_cleared += rows_cleared
    return total_rows_cleared

def lose(score):
    print("You lost!")
    print("Score: ", score)
    exit(0)

def draw_ui(held, next_tetr, score, screen):
    ui_area = pygame.Rect(block_size * grid_size[0], 0, 400, height)
    ui_color = (20, 20, 20)
    pygame.draw.rect(screen, ui_color, ui_area)

    hb_text = font_big.render("Held block:", True, (255, 255, 255))
    screen.blit(hb_text, (width - 280, 150))
    if held != -1:
        held_block = Tetromino(None, held)
        for i in held_block.coords:
            held_block._resolve_rect(i).move_ip(width - 450, 200)
        held_block.draw(screen, False)

    nb_text = font_big.render("Next:", True, (255, 255, 255))
    screen.blit(nb_text, (width - 280, 350))
    for i in range(len(next_tetr)):
        draw_me = Tetromino(None, next_tetr[i])
        for j in draw_me.coords:
            draw_me._resolve_rect(j).move_ip(width - 450, 400 + 200 * i)
        draw_me.draw(screen, False)

    score_view = font_small.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_view, (width - 380, 20))
    return

def json_encode_state(cur_block, block_queue, held_block_type, swapped, bottom_rects, score, delta_score):
    state = {}
    state['board'] = [[(0 if bottom_rects[i][j] == None else 1)for i in range(grid_size[0])] for j in range(grid_size[1])]
    state['cur_block'] = cur_block.blocktype if cur_block is not None else -1
    state['swapped'] = swapped
    state['queue'] = [i for i in block_queue]
    state['held_block'] = held_block_type
    state['delta_score'] = delta_score
    return json.dumps(state)


def main(json_state = "", hardcode_speed = -1, headless = False, headless_input = None):
    #    print(hex(id(headless_input)))
    tetr_queue = deque([random.randint(0, 6),random.randint(0, 6),random.randint(0, 6)])
    held_block_type = -1
    frames = 0
    speed = 25
    score = 0
    swapped = False
    screen = None
    bottom_rects = [[None for i in range(grid_size[1])] for j in range(grid_size[0])]
    cur_block = Tetromino(bottom_rects, 1)
    if not headless:
        screen = pygame.display.set_mode(size)
#    else:
        #        tty.setcbreak(sys.stdin.fileno())
    if json_state != "":
        state = json.loads(json_state)
        for i in range(len(state['board'])):
            for j in range(len(state['board'][i])):
                if state['board'][i][j] == 1:
                    bottom_rects[j][i] = (140, 140 ,140)
        cur_block = Tetromino(bottom_rects, state['cur_block'])
        tetr_queue = deque(state['queue'])
        held_block_type = state['held_block']
    while 1:
        #framerate cap
        if not headless:
            clock.tick(fps)
        frames += 1

        #handle events
        if headless:
            for event in headless_input:
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keypress = event.key
                    if keypress == pygame.K_a or keypress == pygame.K_LEFT:
                    #    print("LEFT")
                        cur_block.move(-1, 0)
                        frames = 0
                    if keypress == pygame.K_d or keypress == pygame.K_RIGHT:
                    #    print("RIGHT")
                        cur_block.move(1, 0)
                        frames = 0
                    if keypress == pygame.K_w or keypress == pygame.K_UP:
                    #    print("UP")
                        cur_block.rotate()
                        frames = 0
                    if keypress == pygame.K_s or keypress == pygame.K_DOWN:
                    #    print("DOWN")
                        score += 2 * cur_block.drop_to_bottom()
                        frames = 0
                    if keypress == pygame.K_LSHIFT:
                    #    print("SHIFT")
                        if swapped == False:
                            held_block_type, cur_block = cur_block.blocktype, Tetromino(bottom_rects, held_block_type)
                            swapped = True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keypress = event.key
                    if keypress == pygame.K_a or keypress == pygame.K_LEFT:
                        #                        print("LEFT")
                        cur_block.move(-1, 0)
                        frames = 0
                    if keypress == pygame.K_d or keypress == pygame.K_RIGHT:
                        #print("RIGHT")
                        cur_block.move(1, 0)
                        frames = 0
                    if keypress == pygame.K_w or keypress == pygame.K_UP:
                        #print("UP")
                        cur_block.rotate()
                        frames = 0
                    if keypress == pygame.K_s or keypress == pygame.K_DOWN:
                        #print("DOWN")
                        score += 2 * cur_block.drop_to_bottom()
                        frames = 0
                    if keypress == pygame.K_LSHIFT:
                        #print("SHIFT")
                        if swapped == False:
                            held_block_type, cur_block = cur_block.blocktype, Tetromino(bottom_rects, held_block_type)
                            swapped = True

        if score > 1000:
            speed = 18
        if score > 2000:
            speed = 14
        if score > 4000:
            speed = 10
        if score > 8000:
            speed = 7
        if hardcode_speed > 0:
            speed = hardcode_speed
            
        delta_score = 0
        if frames % speed == 0:
            cur_block.drop()
            delta_score = 1
            delta_score += [0, 100, 300, 500, 800][sweep_rows(bottom_rects)]
            score += delta_score
            if not cur_block.valid:
                del cur_block
                cur_block = Tetromino(bottom_rects, tetr_queue.popleft())
                tetr_queue.append(random.randint(0, 6))
                swapped = False
                if cur_block._is_bottom():
                    yield(json.dumps({"LOSS":score}))

        if not headless:
            screen.fill(black)
            cur_block.draw(screen)
            for i in range(len(bottom_rects)):
                for j in range(len(bottom_rects[i])):
                    if bottom_rects[i][j] is not None:
                        pygame.draw.rect(screen, bottom_rects[i][j], 
                                pygame.Rect(i * block_size, j * block_size, block_size, block_size))
            draw_ui(held_block_type, tetr_queue, score, screen)
            pygame.display.flip()
        #else:
        #    print("Held block: ", held_block_type)
        #    print("Queue: ", tetr_queue)
        #    print("Score: ", score)
        #    print("Cur Block:", cur_block.blocktype)
        #    for i in range(len(bottom_rects)):
        #        for j in range(len(bottom_rects[i])):
        #            if bottom_rects[i][j] is not None:
        #                print("X", end=" ")
        #            else:
        #                print("_", end=" ")
        #        print("")
        yield json_encode_state(cur_block, tetr_queue, held_block_type, swapped, bottom_rects, score, delta_score)
