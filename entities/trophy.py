import pygame
import numpy as np
import glob
from entities.base import AnimatedSprite


images_path = sorted(glob.glob('./resources/trophy_sparkle_*.png'))
trophy_im_dict = {'sparkle':[pygame.transform.scale(pygame.image.load(img_path),(400,400)) for img_path in images_path]}

class Trophy(AnimatedSprite):
    def __init__(self, position, image_dict, hold_for_n_frames=3,):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.initial_position = position
        self.frames_alive = 0

    def update(self):
        super().next_frame()






