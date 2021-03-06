from __future__ import annotations
from enum import Enum

import pygame
import numpy as np
import datetime
import math
import glob

from typing import Tuple, Dict, List, Optional
from entities.base import AnimatedSprite
from pygame.math import Vector2
from lineup import Lineup

# default faces right
BASE_CUSTOMER_WALKING_ANIMATIONS = [
    [pygame.image.load(p) for p in sorted(glob.glob(f'./resources/customer_walking_*.png'))],
    [pygame.image.load(p) for p in sorted(glob.glob(f'./resources/customer1_walking_*.png'))],
    [pygame.image.load(p) for p in sorted(glob.glob(f'./resources/customer2_walking_*.png'))],
    [pygame.image.load(p) for p in sorted(glob.glob(f'./resources/customer3_walking_*.png'))],
]

ACCESSORIES_DICT_HAIR = {
    'short': ((0,0), pygame.image.load(f'./resources/customerhair_short.png')),
    'bobcut': ((0,0), pygame.image.load(f'./resources/customerhair_bobcut.png')),
    'bun': ((0,0), pygame.image.load(f'./resources/customerhair_newmanbun.png')),
    'karen': ((0,0), pygame.image.load(f'./resources/customerhair_assymmetricbob.png'))
    ,
}

ACCESSORIES_DICT_FACE = {
    'beard': ((0,0), pygame.image.load(f'./resources/customeraccessories_beardnew.png')),
    'mustache': ((0,0), pygame.image.load(f'./resources/customeraccessories_mustachenew.png')),
    'shades': ((0,0), pygame.image.load(f'./resources/customeraccessories_shadesnew.png')),
    'lipstick': ((0,0), pygame.image.load(f'./resources/customeraccessories_lipstick.png')),
}

ACCESSORIES_DICT = {
    'drink_large_straw': ((0,0), pygame.image.load(f'./resources/drink_large_straw.png'))
}

def get_randomized_customer_image_dict():
    random_i = np.random.choice(len(BASE_CUSTOMER_WALKING_ANIMATIONS))
    return {'walking': BASE_CUSTOMER_WALKING_ANIMATIONS[random_i]}


class CustomerType(Enum):
    default = 'default'
    karen = 'karen'
    hipster = 'hipster'

def get_accessory_keys_randomly(customer_type: CustomerType):
    karen_keys = {'karen','lipstick','shades'}
    hipster_keys = {'beard', 'shades', 'bun', 'mustache'}
    if customer_type == CustomerType.default:
        resl = []
        for d in [ACCESSORIES_DICT_FACE, ACCESSORIES_DICT_HAIR]:
            potential_keys = list(set(d.keys()) - karen_keys - hipster_keys)
            # adding None because sometimes people don't have shit on their faces
            resl.append(np.random.choice(potential_keys + [None] * len(d)))
        return set([s for s in resl if s is not None])
    elif customer_type == CustomerType.karen:
        return karen_keys
    elif customer_type == CustomerType.hipster:
        return hipster_keys
    return {}

def get_speed(customer_type: CustomerType):
    if customer_type == CustomerType.default:
        return 3 + np.random.randint(2,6)  # pixels/minute
    elif customer_type == CustomerType.karen:
        return 12
    elif customer_type == CustomerType.hipster:
        return 1 + np.random.randint(2,4)
    return 7

def get_preference_generator(customer_type: CustomerType) -> CustomerPreferenceGenerator:
    if customer_type == CustomerType.karen:
        return KarenPreferenceGenerator()
    if customer_type == CustomerType.hipster:
        return HipsterPreferenceGenerator()
    return CustomerPreferenceGenerator()


class Customer(AnimatedSprite):
    class CustomerState(Enum):
        WALKING = 'walking'

    def __init__(self,
                 position: Tuple[int, int],
                 arrival_time_generator: CustomerArrivalTimeGenerator,
                 customer_type: CustomerType,
                 lineup: Lineup,
                 hold_for_n_frames=1,
                 image_dict: Dict[str, List[pygame.image]] = None,
                 accessory_images=None,
                 visible_accessories=None):

        # initialize some stuff prior to AnimatedSprite
        if image_dict is None:
            image_dict = get_randomized_customer_image_dict()
        if accessory_images is None and visible_accessories is None:
            accessory_images = {
                **ACCESSORIES_DICT,
                **ACCESSORIES_DICT_HAIR,
                **ACCESSORIES_DICT_FACE,
            }
            visible_accessories = get_accessory_keys_randomly(customer_type)

        super().__init__(position, image_dict, hold_for_n_frames=hold_for_n_frames,
                         accessory_images=accessory_images, visible_accessories=visible_accessories)
        self.spawn_location = position
        self.arrival_time = arrival_time_generator.sample()
        self.speed = get_speed(customer_type)
        self.has_lemonade = False
        self.has_seen_recipe = False
        self.likes_recipe = True
        self.reason = ''
        self.set_preferences(get_preference_generator(customer_type))
        self.destination = lineup.last_loc
        self.queue_position = lineup.n_positions + 1

    def set_preferences(self, pref_generator):
        self.min_sugar_conc = pref_generator.sugar_width * np.random.randn() + pref_generator.min_sugar
        self.max_sugar_conc = pref_generator.sugar_width * np.random.randn() + pref_generator.max_sugar
        self.min_lemon_conc = pref_generator.lemon_width * np.random.randn() + pref_generator.min_lemon
        self.max_lemon_conc = pref_generator.lemon_width * np.random.randn() + pref_generator.max_lemon
        self.min_ice_conc = pref_generator.ice_width * np.random.randn() + pref_generator.min_ice
        self.max_ice_conc = pref_generator.ice_width * np.random.randn() + pref_generator.max_ice
        self.min_volume = pref_generator.volume_width * np.random.randn() + pref_generator.min_volume
        self.max_volume = pref_generator.volume_width * np.random.randn() + pref_generator.max_volume
        self.max_spend = pref_generator.spend_width * np.random.randn() + pref_generator.spend_per_ml
        self.straw_preference = np.random.choice(pref_generator.straw_prefs, p = pref_generator.straw_pref_probs)

    def update_destination(self, 
                            timedelta, 
                            lineup, 
                            recipe, 
                            price, 
                            customer_outcomes, 
                            customer_thoughts,
                            customers_in_line,
                            customers_not_in_line,
                            sound):
        if self.queue_position == -1:
            self.kill()
        # Try to get in line
        if self.destination == lineup.last_loc and self.queue_position == lineup.n_positions + 1:
            if not lineup.spots[lineup.n_positions-1].is_occupied: # take spot, destination unchanged
                # import ipdb; ipdb.set_trace()
                customers_in_line.add(self)
                customers_not_in_line.remove(self)
                self.queue_position = lineup.n_positions - 1
                lineup.spots[self.queue_position].is_occupied = True
                lineup.spots[self.queue_position].occupant = self
            else: # If you can't get in line, go home
                self.destination = self.spawn_location
                self.queue_position = -1
                # self.state = 'sad'
                customer_outcomes.append('Line Too Long')

        # If you're in line, try to move up in line
        elif self.queue_position > 0 and not lineup.spots[self.queue_position-1].is_occupied:
            lineup.spots[self.queue_position].is_occupied = False # vacate current spot
            lineup.spots[self.queue_position].occupant = None
            self.queue_position -=1
            lineup.spots[self.queue_position].occupant = self
            lineup.spots[self.queue_position].is_occupied = True # occupy next spot
            self.destination = lineup.spots[self.queue_position].loc

        # If you've made it to the front of the line get lemonade or go home
        elif self.queue_position == 0:
            if not self.has_seen_recipe:
                self.likes_recipe, self.reason = self.customer_likes_recipe(recipe, price, sound)
                if not self.likes_recipe:
                    customer_thoughts.append([id(self), self.reason])
                self.has_seen_recipe = True
            if not self.likes_recipe: # Go home
                self.destination = self.spawn_location
                self.queue_position = -1
                customers_in_line.remove(self)
                customers_not_in_line.add(self)
                lineup.spots[0].is_occupied = False
                lineup.spots[0].occupant = None
                customer_outcomes.append('Bad Experience')
            if self.has_lemonade:
                self.show_accessory('drink_large_straw')
                # self.state = 'lemonade'
                self.destination = self.spawn_location
                self.queue_position = -1
                lineup.spots[0].is_occupied = False
                lineup.spots[0].occupant = None
                customers_in_line.remove(self)
                customers_not_in_line.add(self)
                customer_outcomes.append('Satisfied Customer')

    def get_displacement(self, timedelta):
        distance = timedelta * self.speed
        vector_to_dest = Vector2((self.destination[0] - self.rect[0]),(self.destination[1] - self.rect[1]))
        distance_to_destination = vector_to_dest.magnitude()
        if distance_to_destination <= distance:
            distance = distance_to_destination
            # print(vector_to_dest)
            return vector_to_dest
        else:
            # print(vector_to_dest)
            vector_to_dest.scale_to_length(distance)
            return vector_to_dest

    def update(self, timedelta, lineup, recipe, price, customer_outcomes, customer_thoughts, customers_in_line,
                            customers_not_in_line, sound):
        super().next_frame()
        if tuple(self.rect[:2]) == self.destination:
            self.update_destination(timedelta, lineup, recipe, price, customer_outcomes, customer_thoughts, customers_in_line,
                            customers_not_in_line, sound)
        displacement = self.get_displacement(timedelta)
        # face left (flip of default right) if not moving
        self.flip = displacement[0] <= 0
        super().move(displacement)

    def customer_likes_recipe(self, recipe, price, sound):
        reason = []
        likes_it = True
        if recipe.lemon_concentration < self.min_lemon_conc:
            reason .append('Flavourless.')
            likes_it = False
        if recipe.lemon_concentration > self.max_lemon_conc:
            reason .append('Too sour.')
            likes_it = False
        if recipe.sugar_concentration < self.min_sugar_conc:
            reason.append('Not sweet enough.')
            likes_it = False
        if recipe.sugar_concentration > self.max_sugar_conc:
            reason.append('Too sweet.')
            likes_it = False
        if recipe.total_volume < self.min_volume:
            reason.append("This won't quench my thirst.")
            likes_it = False
        if recipe.total_volume > self.max_volume:
            reason.append('Who could even lift that?')
            likes_it = False
        if recipe.ice_concentration < self.min_ice_conc:
            reason.append(' Too stingy with the ice.')
            likes_it = False
        if recipe.ice_concentration > self.max_ice_conc:
            reason.append(" That's mostly ice!")
            likes_it = False
        if self.straw_preference == 'needs_straw':
            if recipe.straw == 'no':
                reason.append('I refuse to buy a drink without a straw.')
                likes_it = False
        if self.straw_preference == 'anti_paper_straw':
            if recipe.straw == 'paper':
                reason.append('Paper straws are garbage.')
                likes_it = False
        if self.straw_preference == 'anti_plastic_straw':
            if recipe.straw == 'plastic':
                reason.append("Save the turtles! PLASTIC STRAWS KILL.")
                likes_it = False
        if self.max_spend < price/recipe.total_volume:
            reason.append('Too expensive.')
            likes_it = False

        # if reason == '':
        #     reason = 'Yum!'
        if not likes_it:
            pass
            # sound.play_sfx(sound.hit)
        return likes_it, reason


class CustomerArrivalTimeGenerator():
    def __init__(self):
        x = np.append(13+1.65*np.random.randn(10000),17+1.25*np.random.randn(10000))
        hist, bin_edges = np.histogram(x, bins=5000, density=True)
        self.input_random = np.cumsum(hist) * np.diff(bin_edges)[0]
        self.output_time = bin_edges[:-1]

    def sample(self):
        time_frac = np.interp(np.random.random(), self.input_random, self.output_time)
        hour = math.floor(time_frac)
        minutes_frac = 60 * (time_frac - hour)
        minute = math.floor(minutes_frac)
        second = math.floor(60 * (minutes_frac - minute))
        return datetime.time(hour, minute, second)


class CustomerPreferenceGenerator:
    min_sugar = 20/350 # g per 350 mL
    max_sugar = 80/350 # g per 350 mL
    sugar_width = 5/350
    min_lemon = 30/350 # mL per 350 mL
    max_lemon = 90/350 # mL per 350 mL
    lemon_width = 5/350
    min_volume = 250 # mL
    max_volume = 1750 # mL
    volume_width = 25
    min_ice = 1/350 # cubes/350 mL
    max_ice = 9/350 # cubes/350 mL
    ice_width = 1/350
    spend_per_ml = 3.00/350 # $/350 mL
    spend_width = 1.00/350
    straw_prefs = ['no_preference', 'needs_straw', 'anti_plastic_straw', 'anti_paper_straw']
    straw_pref_probs = [0.4, 0.3, 0.15, 0.15]


class HipsterPreferenceGenerator(CustomerPreferenceGenerator):
    min_lemon = 60 / 350  # mL per 350 mL
    max_lemon = 120 / 350  # mL per 350 mL
    lemon_width = 30 / 350
    straw_prefs = ['no_preference', 'needs_straw', 'anti_plastic_straw', 'anti_paper_straw']
    straw_pref_probs = [.5, 0., .5, 0.]
    spend_per_ml = 15.00/350
    spend_width = 5./350


class KarenPreferenceGenerator(CustomerPreferenceGenerator):
    min_sugar = 60/350 # g per 350 mL
    max_sugar = 120/350 # g per 350 mL
    sugar_width = 10/350
    straw_prefs = ['no_preference', 'needs_straw', 'anti_plastic_straw', 'anti_paper_straw']
    straw_pref_probs = [0., .5, 0., .5]
