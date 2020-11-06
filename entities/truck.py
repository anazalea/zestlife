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
        self.speed = -8/(max(1, np.random.poisson(2)))
        self.destination = TRUCT_DESTINATION_LOCATION
        self.frames_at_destination = 0
        self.unload_n_frames = 60
        self.unloading = False

    def update(self, sound):

        if self.rect[0] <= self.destination[0]:
            if self.frames_at_destination == 0:
                sound.play_sfx(sound.pipe)
            self.frames_at_destination += 1
            if self.frames_at_destination > self.unload_n_frames:
                super().move(Vector2(self.speed/2,0))
                self.unloading = False
            else:
                self.unloading = True
        else:
            super().move(Vector2(self.speed,0))        
        
        if self.rect[0] < -1*self.image.get_width():
            self.kill()

class FleetOfTrucks():
    def __init__(self):
        self.trucks = pygame.sprite.Group([])
        self.orders_shipped = []
        self.open_storage_img = pygame.image.load(f'./resources/storage-right-open.png')

    def update(self, lemonade_stand, current_datetime, sound):
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
        self.trucks.update(sound)

    def draw(self, screen):
        # open garage doors
        if any(t.unloading for t in self.trucks):
            screen.blit(self.open_storage_img, (230, 199))

        self.trucks.draw(screen)



