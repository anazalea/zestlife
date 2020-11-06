import pygame
import numpy as np
import datetime
from pygame.math import Vector2
from entities.base import AnimatedSprite

truck_image_dict = {'driving_lemons': [pygame.transform.flip(pygame.image.load('./resources/truck.png'), True, False)]}

class Truck(AnimatedSprite):
    def __init__(self, position, image_dict,hold_for_n_frames=3,):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.speed = -8
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

class FleetOfTrucks():
    def __init__(self):
        self.trucks = pygame.sprite.Group([])
        self.orders_shipped = []

    def update(self, lemonade_stand, current_datetime):
        for order in lemonade_stand.lemonstock.pending_orders:
            if order.delivery_dt - datetime.timedelta(minutes=82) <= current_datetime \
                and not id(order) in self.orders_shipped:
                self.orders_shipped.append(id(order))
                self.trucks.add(Truck((800,240),truck_image_dict))
        for order in lemonade_stand.sugarstock.pending_orders:
            if order.delivery_dt - datetime.timedelta(minutes=82) <= current_datetime \
                and not id(order) in self.orders_shipped:
                self.orders_shipped.append(id(order))
                self.trucks.add(Truck((800,240),truck_image_dict))
        for order in lemonade_stand.icestock.pending_orders:
            if order.delivery_dt - datetime.timedelta(minutes=82) <= current_datetime \
                and not id(order) in self.orders_shipped:
                self.orders_shipped.append(id(order))
                self.trucks.add(Truck((800,240),truck_image_dict))
        self.trucks.update()

    def draw(self, screen):
        self.trucks.draw(screen)



