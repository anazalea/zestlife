import pygame
import numpy as np
from pygame.math import Vector2
from entities.base import AnimatedSprite

truck_image_dict = {'driving_lemons': [pygame.transform.flip(pygame.image.load('./resources/truck.png'), True, False)]}

class Truck(AnimatedSprite):
    def __init__(self, position, image_dict,hold_for_n_frames=3,):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.speed = -4
        self.destination = (150,230)
        self.frames_at_destination = 0
        self.unload_n_frames = 60

    def update(self):

        if self.rect[0] <= self.destination[0]:
            self.frames_at_destination += 1
            if self.frames_at_destination > self.unload_n_frames:
                super().move(Vector2(self.speed/2,0))
        else:
            super().move(Vector2(self.speed,0))        
        
        if self.rect[0] < -1*self.image.get_width():
            self.kill()

