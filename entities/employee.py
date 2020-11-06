import pygame
import numpy as np
from entities.base import AnimatedSprite


class Employee(AnimatedSprite):
    def __init__(self, position, image_dict,
                 work_start_time, work_end_time, hold_for_n_frames=3,daily_wage=20):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time
        self.daily_wage = daily_wage # $/day

    def update(self):
        super().next_frame()

    def set_daily_wage(self, new_wage):
        self.daily_wage = new_wage

    def get_daily_wage(self):
        return self.daily_wage
