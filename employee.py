import pygame
import numpy as np


class Employee():
    def __init__(self):
        self.pose_index = 0
        self.frames_at_pose = 0
        self.image = pygame.image.load(f'./resources/juggle{str(self.pose_index)}.png')
        self.loc = [100,0]
    
    def update(self):
        self.frames_at_pose += 1
        if self.frames_at_pose > 1:
            self.pose_index +=1
            if self.pose_index > 4:
                self.pose_index = 0
            self.frames_at_pose = 0
            self.image = pygame.image.load(f'./resources/juggle{str(self.pose_index)}.png')
    
