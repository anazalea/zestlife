import datetime
import glob
import numpy as np
import pygame
from pygame import draw
from pygame.draw import rect

import menus
from dailychores import get_starting_customers, end_day, track_day_start_stats
from entities.lemonadestand import LemonadeStand
from entities.analog_clock import AnalogClock
from entities.background_sky import BackgroundSky
from entities.town import Town
from menus import FONT_STYLE
from entities.scenery import Town, Trees
from entities.truck import FleetOfTrucks
from entities.customer import CustomerArrivalTimeGenerator
from recipe import Recipe
from temperature import get_temperature
from inventory import Order
from typing import List, Tuple, Optional

KAREN_PROB = .1
HIPSTER_PROB = .1

ice_img = pygame.image.load(f'./resources/ice_cube.png')
lemon_img = pygame.image.load(f'./resources/lemon.png')
sugar_img = pygame.image.load(f'./resources/sugar.png')
straw_img = pygame.image.load(f'./resources/straw.png')
stat_bar_bg_img = pygame.image.load(f'./resources/inventory_mini_stat.png')
clock_img = pygame.image.load(f'./resources/clock_face.png')
thermo_img = pygame.image.load(f'./resources/thermometer.png')


def get_earliest_order_stats(orders: List[Order]) -> Tuple[Optional[datetime.datetime], Optional[float]]:
    if len(orders) == 0:
        return (None, None)
    earliest_order = min(orders)
    return (earliest_order.delivery_dt, earliest_order.amount)


def get_compact_rep_timedelta(tdelta: datetime.timedelta) -> str:
    return '%.0f H' % (tdelta.seconds / 3600)



class LemonadeGame():
    def __init__(self, sound, config=None):
        self.sound = sound
        self.arrival_time_generator = CustomerArrivalTimeGenerator()

        # employee
        employee_image_dict = {}
        for s in ['juggle','shake','watch']:
            images_path = sorted(glob.glob(f'./resources/employee_{s}_*'))
            employee_image_dict[s] = [pygame.image.load(img_path) for img_path in images_path]
        self.employee_image_dict = employee_image_dict
        self.screen = pygame.display.set_mode((800, 600))
        self.current_datetime = datetime.datetime(2020,6,10,10)
        self.background_sky = BackgroundSky(self.current_datetime.time(), self.screen)
        self.lemonade_stand = LemonadeStand(self.screen, self.current_datetime, self.employee_image_dict, sound, n_employees=3)
        self.analog_clock = AnalogClock(self.current_datetime.time(), self.screen)
        self.town = Town(self.current_datetime.time())
        self.trees = Trees()
        self.customer_outcomes = []
        self.word_of_mouth_effect = 0
        self.impending_shipments = []
        self.trucks = FleetOfTrucks()
        self.recipe = Recipe(lemon_juice=40, sugar=35, water=300, ice=5, straw='no') # initial recipe should be part of config

        customers = self.get_starting_customers()
        track_day_start_stats(self)
        self.future_customers = pygame.sprite.Group(customers)
        self.active_customers = pygame.sprite.Group([])
        self.daily_report = {}

    def get_starting_customers(self):
        return get_starting_customers(
            dt=self.current_datetime.date(),
            word_of_mouth_effect=self.word_of_mouth_effect,
            arrival_time_generator=self.arrival_time_generator,
            customer_karen_prob=KAREN_PROB,
            customer_hipster_prob=HIPSTER_PROB,
            lineup=self.lemonade_stand.lineup,
        )

    def update_world(self, game_speed_in_minutes: float):
        """Updates state to next state given game_speed."""
        old_datetime = self.current_datetime
        self.lemonade_stand.workforce.update()
        self.current_datetime += datetime.timedelta(minutes=game_speed_in_minutes)
        self.town.update_town_time(self.current_datetime.time())
        self.background_sky.update_color(self.current_datetime.time())
        self.analog_clock.current_time = self.current_datetime.time()
        # check for new orders
        self.trucks.update(self.lemonade_stand, self.current_datetime)

        # if it's the end of the day, recap, setup for tomorrow
        if not self.current_datetime.date() == old_datetime.date():
            print('END OF DAY')
            outcomes, word_of_mouth_effect, self.daily_report = end_day(self)
            print(outcomes)
            self.word_of_mouth_effect = word_of_mouth_effect
            self.customer_outcomes = []
            customers = self.get_starting_customers()
            track_day_start_stats(self)
            self.future_customers = pygame.sprite.Group(customers)
            self.active_customers = pygame.sprite.Group([])
            self.lemonade_stand.lineup.clear()
            menus.daily_report_menu(self)

        # check for new customers arriving, add them to the update group
        for customer in self.future_customers.sprites():
            if customer.arrival_time < self.current_datetime.time():
                self.future_customers.remove(customer)
                self.active_customers.add(customer)
        self.lemonade_stand.update(self.current_datetime, game_speed_in_minutes, self.recipe)
        self.active_customers.update(game_speed_in_minutes, self.lemonade_stand.lineup,
                                     self.recipe, self.lemonade_stand.price, self.customer_outcomes)

    def draw(self):
        self.screen.blit(self.background_sky.background, (0,0))
        self.town.draw(self.screen)
        self.trucks.draw(self.screen)
        self.trees.draw(self.screen)
        self.lemonade_stand.draw(self.current_datetime.time(),
                                    self.screen)
        self.active_customers.draw(self.screen)


    def print_stats(self):
        font = pygame.font.Font(FONT_STYLE, 14)  # Edit fonts here
        txt_color = (255, 255, 255)

        # time_stamp = font.render(
        #     '{datetimstr} ({temp_txt} Celcius)'.format(
        #         datetimstr=self.current_datetime.strftime('%Y-%m-%d %H:%M %p'),
        #         temp_txt=get_temperature(self.current_datetime)
        #     ), 1, txt_color)
        # current_price = font.render(str(self.lemonade_stand.price) + ' $ / CUP', 1, txt_color)

        margin = 32
        img_size = 24
        self.screen.blit(pygame.transform.scale(stat_bar_bg_img, (270, 65)), [10, 530])
        icon_imgs = [
            lemon_img,
            sugar_img,
            ice_img
        ]
        stocks = [
            self.lemonade_stand.lemonstock,
            self.lemonade_stand.sugarstock,
            self.lemonade_stand.icestock
        ]
        # draw icons
        for i, img in enumerate(icon_imgs):
            self.screen.blit(pygame.transform.scale(img, (img_size, img_size)),
                             [20 + (img_size + margin) * i, 540])
        # draw values
        for i, stock in enumerate(stocks):
            self.screen.blit(
                font.render('%.0f' % stock.current_units, 1, txt_color),
                [20 + (img_size + margin) * i, 565]
            )
        # draw money
        money = self.lemonade_stand.account_balance
        money_color = (0, 255, 0) if money > 0 else (255, 0, 0)
        self.screen.blit(
            font.render('$ %.2f' % money, 1, money_color),
            [20 + (img_size + margin) * len(stocks), 565]
        )
        # draw countdown
        countdown_offset = 505
        any_pending_orders = False
        for i, stock in enumerate(stocks):
            delivery_dt, amount = get_earliest_order_stats(stock.pending_orders)
            time_to_next_order_string = ''
            if delivery_dt is not None:
                any_pending_orders = True
                time_to_next_order_string = get_compact_rep_timedelta(delivery_dt - self.current_datetime)
            self.screen.blit(
                font.render(time_to_next_order_string, 1, txt_color),
                [20 + (img_size + margin) * i, countdown_offset]
            )
            amount_of_next_order_string = ''
            if amount is not None:
                amount_of_next_order_string = '+ %.0f' % amount
            self.screen.blit(
                font.render(amount_of_next_order_string, 1, txt_color),
                [20 + (img_size + margin) * i, countdown_offset - 20]
            )
        if any_pending_orders:
            self.screen.blit(
                font.render('Pending Order', 1, txt_color),
                [20, countdown_offset - 40]
            )

        # temperature
        temp = get_temperature(self.current_datetime)
        temp_color = (max(17 * (temp - 15), 255), 0, 0) if temp > 25 else (0, 0, 0)
        temp_txt = font.render(str(temp), 1, temp_color)
        self.screen.blit(thermo_img, [0, 5])
        self.screen.blit(temp_txt, [40, 20])

        # clock
        self.analog_clock.draw(self.screen)

