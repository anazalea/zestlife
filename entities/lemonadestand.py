import pygame
import datetime
from entities.employee import Employee
from lineup import Lineup

class LemonadeStand():
    def __init__(self, screen, n_employees=0):
        self.image_open = pygame.image.load('./resources/stand.png')
        self.image_closed = pygame.image.load('./resources/stand_closed.png')
        self.im_height = self.image_open.get_height()
        self.im_width = self.image_open.get_width()
        self.loc = [int((screen.get_width()-self.im_width)/2), int((screen.get_height()-self.im_height)/1.5)]
        self.opening_time = datetime.time(8)
        self.closing_time = datetime.time(20)
        self.juicing_efficiency = 45 # mL/lemon
        self.lemons = 100 # lemons
        self.sugar = 100 # g
        self.ice = 200
        self.price = 2.00 # $
        self.account_balance = 0.00 # $
        self.lineup = Lineup([250,250], [700,250],9)
        self.prep_time = 30 # minutes/lemonade
        self.employees = []


    def make_a_sale(self, customer):
        pass


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
        print('CHECKING INVENTORY')
        if self.lemons * self.juicing_efficiency < recipe.lemon_juice:
            return False
        if self.sugar < recipe.sugar:
            return False
        if self.ice < recipe.ice:
            return False
        else:
            return True
