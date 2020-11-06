import pygame
import numpy as np
import datetime
from datetime import date
from entities.base import AnimatedSprite


class Employee(AnimatedSprite):
    def __init__(self, position, image_dict,
                 work_start_time, work_end_time, hold_for_n_frames=3,daily_wage=20):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time
        self.daily_wage = daily_wage # $/day
        self.started_work = datetime.time(8)
        self.ended_work = datetime.time(20)

    def update(self):
        super().next_frame()

    def set_daily_wage(self, new_wage):
        self.daily_wage = new_wage

    def get_daily_wage(self):
        return self.daily_wage

    def clock_in(self, current_time):
        self.started_work = current_time

    def clock_out(self, current_time):
        self.ended_work = current_time

    def get_owed_wages(self):
        time_worked = datetime.datetime.combine(date.min, self.ended_work) - datetime.datetime.combine(date.min, self.started_work)
        hourly_wage = self.daily_wage / 12
        print(time_worked)
        return time_worked.seconds * hourly_wage / 3600
