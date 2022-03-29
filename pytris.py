import sys
import random
import copy
import pygame
import math

pygame.init()

#global variables (OOH SCARY)
size = width, height = 600, 840 
speed = 60
black = 0, 0, 0
fps = 5
block_size = 30
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

cur_block = None
bottom_rects = []
bottom_rects_draw = []


#TODO: move blocks into this class
class Block:
    valid = True
    rects = []
    color = (255, 255, 255)
    def __init__(self, blocktype):
        if blocktype == 0: #Z
            self.color = (255, 0, 0)
            self.rects = [
            pygame.Rect(0, 0, block_size, block_size),
            pygame.Rect(block_size, block_size, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(block_size, block_size * 2, block_size, block_size)
        ]
            return
        elif blocktype == 1: #T
            self.color = (255, 0, 255)
            self.rects = [
            pygame.Rect(block_size, 0, block_size, block_size),
            pygame.Rect(block_size, block_size, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(block_size * 2, block_size, block_size, block_size)
        ]
            return
        elif blocktype == 2: #S
            self.color = (0, 255, 0)
            self.rects = [
            pygame.Rect(block_size, 0, block_size, block_size),
            pygame.Rect(block_size, block_size, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(0, block_size * 2, block_size, block_size)
        ]
            return
        elif blocktype == 3: #I
            self.color = (120, 120, 255)
            self.rects = [
            pygame.Rect(0, 0, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(0, block_size * 2, block_size, block_size),
            pygame.Rect(0, block_size * 3, block_size, block_size)
        ]
            return
        elif blocktype == 4: #L
            self.color = (255, 120, 0)
            self.rects = [
            pygame.Rect(0, 0, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(0, block_size * 2, block_size, block_size),
            pygame.Rect(block_size, block_size * 2, block_size, block_size)
        ]
            return
        elif blocktype == 5: #J
            self.color = (0, 0, 255)
            self.rects = [
            pygame.Rect(block_size, 0, block_size, block_size),
            pygame.Rect(block_size, block_size, block_size, block_size),
            pygame.Rect(block_size, block_size * 2, block_size, block_size),
            pygame.Rect(0, block_size * 2, block_size, block_size)
        ]
            return
        elif blocktype == 6: #O
            self.color = (255, 255, 0)
            self.rects = [
            pygame.Rect(0, 0, block_size, block_size),
            pygame.Rect(0, block_size, block_size, block_size),
            pygame.Rect(block_size, 0, block_size, block_size),
            pygame.Rect(block_size, block_size, block_size, block_size)
        ]
            return
        else:
            self.valid = False

    def move(self, x, y):
        if not self.valid:
            return
        for i in self.rects:
            i.move_ip(x, y)
        if self._is_offscreen():
            for i in self.rects:
                i.move_ip(-x, -y)
        return

    def drop(self):
        if not self.valid:
            return
        for i in self.rects:
            i.move_ip(0, block_size)
        if self._is_bottom():
            print("at bottom")
            for i in self.rects:
                i.move_ip(0, -block_size)
            self._delete_self()
        return

    def rotate(self):
        if not self.valid:
            return
        for i in self.rects:
            #rotate logic
            pass
        return

    def drop_to_bottom(self):
        if not self.valid:
            return
        return

    def touch_bottom(self):
        if not self.valid:
            return
        return
    
    def draw(self):
        if not self.valid:
            return
        for i in self.rects:
            pygame.draw.rect(screen, self.color, i)

    def _is_bottom(self):
        for i in self.rects:
            if i.collidelistall(bottom_rects):
                return True
            if i.bottom > height:
                return True
        return False

    def _is_offscreen(self):
        for i in self.rects:
            if i.left < 0 or i.right > width:
                return True
        return False

    def _delete_self(self):
        self.valid = False
        return
    def __del__(self):
        print("deleting self")
        for i in self.rects:
            bottom_rects.append(i)
            bottom_rects_draw.append((self.color, i))
            self.valid = False
        return

#   def is_offscreen(block):
#       for i in block[1]:
#           if(i.top < height):
#               return False 
#       return True 

#   def is_bottom(block):
#       for i in block[1]:
#           if i.collidelistall(bottom_rects):
#               return True
#           if i.bottom > height:
#               return True
#       return False

#   def is_offscreen(block):
#       for i in block[1]:
#           if i.collidelistall(bottom_rects):
#               return True
#           if i.left < 0 or i.right > width:
#               return True
#       return False

#   def move_block(block, x, y):
#       if block == None:
#           return
#       for i in range(len(block[1])):
#           block[1][i] = block[1][i].move(x, y)
#       if is_offscreen(block):
#           for i in range(len(block[1])):
#               block[1][i] = block[1][i].move(-x, -y)

#   def drop_block(block):
#       if block == None:
#           return
#       for i in range(len(block[1])):
#           block[1][i] = block[1][i].move(0, speed)

#TODO
#   def rotate_block(block):
#       if block == None:
#           return

#TODO
#   def drop_to_bottom(block):
#       return

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
            

        cur_block.drop()
        if not cur_block.valid:
            del cur_block
            cur_block = Block(random.randint(0, 6))
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
