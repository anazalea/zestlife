import pygame
import numpy as np

from entities.base import AnimatedSprite


class Stars(AnimatedSprite):
    def __init__(self):
        self.twinkle_state = 0
        self.frames_at_twinkle_state = 0
        self.image = pygame.image.load(f'./resources/stars{str(self.twinkle_state)}.png')
    
    def twinkle(self):
        self.frames_at_twinkle_state += 1
        if self.frames_at_twinkle_state > 3:
            self.twinkle_state +=1
            if self.twinkle_state > 1:
                self.twinkle_state = 0
            self.frames_at_twinkle_state = 0
            self.image = pygame.image.load(f'./resources/stars{str(self.twinkle_state)}.png')

    def update(self):
        pass
    

class Sun(AnimatedSprite):
    def __init__(self):
        self.twinkle_state = 0
        self.frames_at_twinkle_state = 0
        self.image = pygame.image.load(f'./resources/sun{str(self.twinkle_state)}.png')
    
    def twinkle(self):
        self.frames_at_twinkle_state += 1
        if self.frames_at_twinkle_state > 3:
            self.twinkle_state +=1
            if self.twinkle_state > 2:
                self.twinkle_state = 0
            self.frames_at_twinkle_state = 0
            self.image = pygame.image.load(f'./resources/sun{str(self.twinkle_state)}.png')

    def update(self):
        pass
    

class Cloud(AnimatedSprite):
    def __init__(self, screen):
        self.image = pygame.image.load('./resources/cloud.png')
        self.speed = 1 + 2.5 * np.random.randn() #pixels/minute
        # TODO: check if we need to pass the whole screen
        self.current_loc = [screen.get_width(), 50+np.random.randint(-100,100)]

    def move(self, time_delta):
        new_loc = [self.current_loc[0]-self.speed*time_delta, self.current_loc[1]]
        if np.random.randn() > 0.2:
            self.speed += (1 + np.random.randn())
        self.current_loc = new_loc

    def update(self):
        pass