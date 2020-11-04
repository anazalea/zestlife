import pygame
import datetime
from entities.employee import Employee
from lineup import Lineup

class LemonadeStand():
    def __init__(self, screen, current_time, n_employees=0,):
        self.image_open = pygame.image.load('./resources/stand.png')
        self.image_closed = pygame.image.load('./resources/stand_closed.png')
        self.im_height = self.image_open.get_height()
        self.im_width = self.image_open.get_width()
        self.loc = [int((screen.get_width()-self.im_width)/2), int((screen.get_height()-self.im_height)/1.5)]
        self.opening_time = datetime.time(8)
        self.closing_time = datetime.time(20)
        self.open = self.is_open(current_time)
        self.juicing_efficiency = 45 # mL/lemon
        self.lemons = 500 # lemons
        self.sugar = 500 # g
        self.ice = 200
        self.price = 2.00 # $
        self.account_balance = 0.00 # $
        self.lineup = Lineup((300,225),(0,250) ,5)
        self.employees = []
        self.prep_time = 30 # minutes/lemonade
        self.time_serving_customer = 0

    def is_open(self, current_time):
        return self.opening_time < current_time < self.closing_time

    def make_a_sale(self, recipe):
        self.lemons -= recipe.lemon_juice / self.juicing_efficiency
        self.ice -= recipe.ice
        self.sugar -= recipe.sugar
        self.account_balance += self.price



    def serve_customer(self, recipe, timedelta):
        if self.lineup.spots[0].is_occupied and \
            self.lineup.spots[0].occupant.likes_recipe and \
                not self.lineup.spots[0].occupant.has_lemonade and \
                self.open and self.has_enough_stuff(recipe):
            self.time_serving_customer += timedelta
            if self.time_serving_customer > self.prep_time:
                self.lineup.spots[0].occupant.has_lemonade = True
                self.time_serving_customer = 0
                self.make_a_sale(recipe)

    def update(self, current_time, timedelta, recipe):
        self.open = self.is_open(current_time)
        self.serve_customer(recipe, timedelta)

    def validate_price(self, value):
        try:
            float(value)
            self.update_price(float(value))
        except:
            print('INVALID LEMONADE PRICE')

    def update_price(self, new_price):
        print('UPDATING PRICE')
        self.price = new_price     
    
    def draw(self, time, screen):
        if time > self.opening_time and time < self.closing_time:
            screen.blit(self.image_open, self.loc)
        else:
            screen.blit(self.image_closed, self.loc)

    def has_enough_stuff(self, recipe):
        if self.lemons * self.juicing_efficiency < recipe.lemon_juice:
            return False
        if self.sugar < recipe.sugar:
            return False
        if self.ice < recipe.ice:
            return False
        else:
            return True
