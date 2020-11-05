import pygame
import numpy as np
import glob
from entities.base import AnimatedSprite
from pygame.math import Vector2

images_path = glob.glob('./resources/coin_*.png')
coin_im_dict = {'spinning':[pygame.image.load(img_path) for img_path in images_path]}

class Coin(AnimatedSprite):
    def __init__(self, position, image_dict, hold_for_n_frames=3,):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.initial_position = position
        self.frames_alive = 0

    def update(self):
        self.move(Vector2(0,-1))
        self.frames_alive += 1
        super().next_frame()

        if self.frames_alive == 50:
            self.kill()



