import datetime
import pygame
import numpy as np
from pygame.math import Vector2
from entities.base import AnimatedSprite

class Town():
    def __init__(self, current_time):
        self.image_day = pygame.image.load('./resources/Background_day.png')
        self.image_night = pygame.image.load('./resources/Background_night.png')
        self.update_town_time(current_time)

    def update_town_time(self, current_time):
        if current_time > datetime.time(20) or current_time < datetime.time(6):
            self.image = self.image_night
        else:
            self.image = self.image_day

    def draw(self, screen):
        screen.blit(self.image, (0,0))


class Trees():
    def __init__(self):
        self.image = pygame.image.load('./resources/trees.png')

    def draw(self, screen):
        screen.blit(self.image, (0,0))

CLOUD_IMAGE_DICT = {'being': [pygame.transform.scale(pygame.image.load('./resources/cloud.png'), (300, 150) )]}

class Cloud(AnimatedSprite):
    def __init__(self, position, hold_for_n_frames=1, load_name=None):
        super().__init__(
            position,
            flip = False,
            image_dict = CLOUD_IMAGE_DICT,
            hold_for_n_frames = hold_for_n_frames,
            state='being',
        )
        self.speed = -1*np.abs((1.5 * np.random.randn()))
        scale = np.random.randint(100,300)
        self.image = pygame.transform.scale(self.image, (scale,int(scale/2)))

    def update(self):
        super().move(Vector2(self.speed,0))        

        if self.rect[0] < -1*self.image.get_width():
            self.kill()


class Clouds():
    def __init__(self, cloudiness=0.25):
        self.clouds = pygame.sprite.Group([])
        self.cloudiness = cloudiness

    def update(self):
        
        self.clouds.update()
        if np.random.uniform() > (1-self.cloudiness/10.):
            self.clouds.add(Cloud((800, np.random.randint(-100,100))))

        