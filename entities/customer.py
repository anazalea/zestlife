from enum import Enum

import pygame
import numpy as np
import datetime
import math

from entities.base import AnimatedSprite
from pygame.math import Vector2


class Customer(AnimatedSprite):
    class CustomerState(Enum):
        HAPPY = 'happy'
        SAD = 'sad'
        LEMONADE = 'lemonade'

    def __init__(self, position, arrival_time_generator, pref_generator, image_dict, hold_for_n_frames=1):
        super().__init__(position, image_dict, hold_for_n_frames)
        self.arrival_time = arrival_time_generator.sample()
        self.speed = 10 + 1.5 * np.random.randn()  # pixels/minute
        self.has_lemonade = False
        self.likes_recipe = True
        self.set_preferences(pref_generator)


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

    def get_displacement(self, timedelta):
        return Vector2(self.speed*timedelta, 0)

    def update(self, timedelta) -> None:
        super().next_frame()
        super().move(self.get_displacement(timedelta))

    def customer_likes_recipe(self, recipe, price):
        reason = ''
        likes_it = True
        if recipe.lemon_concentration < self.min_lemon_conc:
            reason += ' Flavourless.'
            likes_it = False
        if recipe.lemon_concentration > self.max_lemon_conc:
            reason += ' Too sour.'
            likes_it = False
        if recipe.sugar_concentration < self.min_sugar_conc:
            reason += ' Not sweet enough.'
            likes_it = False
        if recipe.sugar_concentration > self.max_sugar_conc:
            reason += ' Too sweet.'
            likes_it = False
        if recipe.total_volume < self.min_volume:
            reason += " This won't quench my thirst."
            likes_it = False
        if recipe.total_volume > self.max_volume:
            reason += ' Who could even lift that?'
            likes_it = False
        if recipe.ice_concentration < self.min_ice_conc:
            reason += ' Too stingy with the ice.'
            likes_it = False
        if recipe.ice_concentration > self.max_ice_conc:
            reason += " That's mostly ice!"
            likes_it = False
        if self.straw_preference == 'needs_straw':
            if recipe.straw == 'no':
                reason += ' I like straws.'
                likes_it = False
        if self.straw_preference == 'anti_paper_straw':
            if recipe.straw == 'paper':
                reason += ' Paper straws are garbage.'
                likes_it = False
        if self.straw_preference == 'anti_plastic_straw':
            if recipe.straw == 'plastic':
                reason += " Won't somebody think of the turtles!?"
                likes_it = False
        if self.max_spend < price/recipe.total_volume:
            reason += ' Not worth the money.'
            likes_it = False
        
        if reason == '':
            reason = 'Yum!'

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

class CustomerPreferenceGenerator():
    def __init__(self):
        self.min_sugar = 20/350 # g per 350 mL
        self.max_sugar = 80/350 # g per 350 mL
        self.sugar_width = 5/350
        self.min_lemon = 30/350 # mL per 350 mL
        self.max_lemon = 90/350 # mL per 350 mL
        self.lemon_width = 5/350
        self.min_volume = 250 # mL
        self.max_volume = 1750 # mL
        self.volume_width = 25
        self.min_ice = 1/350 # cubes/350 mL
        self.max_ice = 9/350 # cubes/350 mL
        self.ice_width = 1/350
        self.spend_per_ml = 3.00/350 # $/350 mL
        self.spend_width = 1.00/350
        self.straw_prefs = ['no_preference', 'needs_straw', 'anti_plastic_straw', 'anti_paper_straw']
        self.straw_pref_probs = [0.4, 0.3, 0.15, 0.15]