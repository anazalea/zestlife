import pygame
import numpy as np
from entities.base import AnimatedSprite

class Employee(AnimatedSprite):
    def __init__(self, position, image_dict, 
                 work_start_time, work_end_time,hold_for_n_frames=1,):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time

    def update(self):
        super().next_frame()

# class Employee():
#     def __init__(self):
#         self.pose_index = 0
#         self.frames_at_pose = 0
#         self.image = pygame.image.load(f'./resources/juggle{str(self.pose_index)}.png')
#         self.loc = [100,0]
    
#     def update(self):
#         self.frames_at_pose += 1
#         if self.frames_at_pose > 1:
#             self.pose_index +=1
#             if self.pose_index > 4:
#                 self.pose_index = 0
#             self.frames_at_pose = 0
#             self.image = pygame.image.load(f'./resources/juggle{str(self.pose_index)}.png')
    
