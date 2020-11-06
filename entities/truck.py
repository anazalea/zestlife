import pygame
import numpy as np
import datetime
from pygame.math import Vector2
from entities.base import AnimatedSprite

TRUCT_DESTINATION_LOCATION = (150,230)

TRUCK_IMAGE_DICT = {
    'driving': [pygame.image.load('./resources/truck.png')]
}

position_load = (25, 16)
def get_load_resized(image):
    return pygame.transform.scale(image, (20, 20))

TRUCK_LOAD_DICT = {
    'lemon': (position_load, get_load_resized(pygame.image.load(f'./resources/lemon_icon.png'))),
    'ice': (position_load, get_load_resized(pygame.image.load(f'./resources/ice_icon.png'))),
    'sugar': (position_load, get_load_resized(pygame.image.load(f'./resources/sugar_icon.png'))),
    'straw': (position_load, get_load_resized(pygame.image.load(f'./resources/straw_icon.png'))),
}

class Truck(AnimatedSprite):
    def __init__(
            self, position, hold_for_n_frames=3, load_name=None
    ):
        super().__init__(
            position,
            flip = True,
            image_dict=TRUCK_IMAGE_DICT,
            hold_for_n_frames=hold_for_n_frames,
            state='driving',
            accessory_images=TRUCK_LOAD_DICT,
            visible_accessories={load_name},
        )
        self.speed = -8
        self.destination = TRUCT_DESTINATION_LOCATION
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
                self.trucks.add(Truck((800,240),load_name='lemon'))
        for order in lemonade_stand.sugarstock.pending_orders:
            if order.delivery_dt - datetime.timedelta(minutes=82) <= current_datetime \
                and not id(order) in self.orders_shipped:
                self.orders_shipped.append(id(order))
                self.trucks.add(Truck((800,240),load_name='sugar'))
        for order in lemonade_stand.icestock.pending_orders:
            if order.delivery_dt - datetime.timedelta(minutes=82) <= current_datetime \
                and not id(order) in self.orders_shipped:
                self.orders_shipped.append(id(order))
                self.trucks.add(Truck((800,240),load_name='ice'))
        self.trucks.update()

    def draw(self, screen):
        self.trucks.draw(screen)



