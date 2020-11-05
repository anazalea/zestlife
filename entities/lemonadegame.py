import datetime
import glob
import numpy as np
import pygame
from dailychores import start_day, end_day
from entities.lemonadestand import LemonadeStand
from entities.analog_clock import AnalogClock
from entities.background_sky import BackgroundSky
from entities.customer import Customer, CustomerArrivalTimeGenerator, CustomerPreferenceGenerator
from entities.town import Town
from recipe import Recipe
from temperature import get_temperature

class LemonadeGame():
    def __init__(self, config=None):
        # customer
        customer_image_dict = {}
        for s in ['walking']:
            images_path = sorted(glob.glob(f'./resources/customer_{s}_*.png'))
            print(images_path)
            customer_image_dict[s+'_right'] = [pygame.image.load(img_path) for img_path in images_path]
            customer_image_dict[s+'_left'] = [pygame.transform.flip(image, True, False) \
                                                    for image in customer_image_dict[s+'_right']]
        self.customer_image_dict = customer_image_dict
        self.arrival_time_generator = CustomerArrivalTimeGenerator()
        self.preference_generator = CustomerPreferenceGenerator()

        # employee
        employee_image_dict = {}
        for s in ['juggle','shake']:
            images_path = sorted(glob.glob(f'./resources/employee_{s}_*'))
            employee_image_dict[s] = [pygame.image.load(img_path) for img_path in images_path]

        self.employee_image_dict = employee_image_dict
        self.screen = pygame.display.set_mode((800, 600))
        self.current_datetime = datetime.datetime(2020,6,10,10)
        self.background_sky = BackgroundSky(self.current_datetime.time(), self.screen)
        self.lemonade_stand = LemonadeStand(self.screen, self.current_datetime.time(), self.employee_image_dict, n_employees=2)
        self.analog_clock = AnalogClock(self.current_datetime.time(), self.screen)
        self.town = Town(self.current_datetime.time())
        # self.scenery = pygame.image.load('./resources/background.png')
        self.customer_outcomes = []
        self.word_of_mouth_effect = 0

        

        self.recipe = Recipe(lemon_juice=40, sugar=35, water=300, ice=5, straw='no') # initial recipe should be part of config

        customers = start_day(self)
        self.future_customers = pygame.sprite.Group(customers)
        self.active_customers = pygame.sprite.Group([])

    def update_world(self, game_speed):
        old_datetime = self.current_datetime
        self.lemonade_stand.workforce.update()
        self.current_datetime += datetime.timedelta(minutes=game_speed)
        self.town.update_town_time(self.current_datetime.time())
        self.background_sky.update_color(self.current_datetime.time())
        self.analog_clock.current_time = self.current_datetime.time()

        # if it's the end of the day, recap, setup for tomorrow
        if not self.current_datetime.date() == old_datetime.date():
            print('END OF DAY')
            outcomes, word_of_mouth_effect = end_day(self)
            print(outcomes)
            self.word_of_mouth_effect = word_of_mouth_effect
            self.customer_outcomes = []
            customers = start_day(self)
            self.future_customers = pygame.sprite.Group(customers)
            self.active_customers = pygame.sprite.Group([])
            self.lemonade_stand.lineup.clear()

        # check for new customers arriving, add them to the update group
        for customer in self.future_customers.sprites():
            if customer.arrival_time < self.current_datetime.time():
                self.future_customers.remove(customer)
                self.active_customers.add(customer)
        self.lemonade_stand.update(self.current_datetime.time(), game_speed, self.recipe)
        self.active_customers.update(game_speed, self.lemonade_stand.lineup, 
                    self.recipe, self.lemonade_stand.price, self.customer_outcomes)

    def draw(self):
        self.screen.blit(self.background_sky.background, (0,0))
        self.town.draw(self.screen)
        # self.screen.blit(self.scenery, (0,0))
        self.lemonade_stand.workforce.draw(self.screen)
        self.lemonade_stand.draw(self.current_datetime.time(),
                                    self.screen)
        self.active_customers.draw(self.screen)


    def print_stats(self):
        font = pygame.font.SysFont('comicsansmsttf',20)
        time_stamp = font.render(
            '{datetimstr} ({tempinc} Celcius)'.format(
                datetimstr=self.current_datetime.strftime('%Y-%m-%d %H:%M %p'),
                tempinc=get_temperature(self.current_datetime)
            ), 1, (214, 26, 13))
        current_price = font.render(str(self.lemonade_stand.price) + ' $ / CUP', 1, (214, 26, 13))
        n_lemons = font.render(str(np.round(self.lemonade_stand.lemons, 1)) + ' LEMONS ON HAND', 1,
                                (214, 26, 13))
        g_sugar = font.render(str(self.lemonade_stand.sugar) + ' g SUGAR ON HAND', 1, (214, 26, 13))
        juice_eff = font.render(
            f'JUICING EFFICIENCY {str(self.lemonade_stand.juicing_efficiency)} mL/lemon', 1,
            (214, 26, 13))
        money = font.render(str(self.lemonade_stand.account_balance) + ' $', 1, (0, 0, 0))
        thoughts = font.render(self.lemonade_stand.recent_customer_thought, 1, (0, 0, 0))

        self.screen.blit(time_stamp, [20, 20])
        self.screen.blit(current_price, [20, 40])
        self.screen.blit(juice_eff, [20, 60])
        self.screen.blit(n_lemons, [20, 80])
        self.screen.blit(g_sugar, [20, 100])
        self.screen.blit(money, [20, 120])
        self.screen.blit(thoughts, [10, 580])

        


