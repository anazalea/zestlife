import datetime
import calendar
import glob
import numpy as np
import pygame
from pygame import draw
from pygame.draw import rect

import menus
import endgame
from dailychores import get_starting_customers, end_day, track_day_start_stats
from entities.lemonadestand import LemonadeStand
from entities.analog_clock import AnalogClock
from entities.background_sky import BackgroundSky
from entities.town import Town
from menus import FONT_STYLE
from entities.scenery import Town, Trees, Clouds
from entities.truck import FleetOfTrucks
from entities.customer import CustomerArrivalTimeGenerator
from recipe import Recipe
from temperature import get_temperature
from inventory import Order
from typing import List, Tuple, Optional

KAREN_PROB = .1
HIPSTER_PROB = .1

RGB_GREEN = (0, 255, 0)
RGB_RED = (255, 0, 0)
RGB_WHITE = (255, 255, 255)

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
        self.start_datetime = datetime.datetime(2020,6,10,10)
        self.current_datetime = self.start_datetime
        self.background_sky = BackgroundSky(self.current_datetime.time(), self.screen)
        self.lemonade_stand = LemonadeStand(self.screen, self.current_datetime, self.employee_image_dict, sound, n_employees=3)
        self.analog_clock = AnalogClock(self.current_datetime.time(), self.screen)
        self.town = Town(self.current_datetime.time())
        self.trees = Trees()
        self.customer_outcomes = []
        self.last_thinking_customer = None
        self.last_customer_thought = ''
        self.customer_thoughts = []
        self.thought_frames = 0
        self.word_of_mouth_effect = 0
        self.impending_shipments = []
        self.trucks = FleetOfTrucks()
        self.clouds = Clouds()
        self.victorious = False
        self.recipe = Recipe(lemon_juice=40, sugar=35, water=300, ice=5, straw='no') # initial recipe should be part of config

        customers = self.get_starting_customers()
        track_day_start_stats(self)
        self.future_customers = pygame.sprite.Group(customers)
        self.active_customers = pygame.sprite.Group([])
        self.customers_in_line = pygame.sprite.Group([])
        self.customers_not_in_line = pygame.sprite.Group([])
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
        if not self.victorious:
            self.victorious = endgame.check_victory_condition(self)
            # if self.victorious:
            #     self.sound.play_sfx(self.sound.victory)
                

        old_datetime = self.current_datetime
        self.lemonade_stand.workforce.update()
        self.current_datetime += datetime.timedelta(minutes=game_speed_in_minutes)
        self.town.update_town_time(self.current_datetime.time())
        self.background_sky.update_color(self.current_datetime.time())
        self.analog_clock.current_time = self.current_datetime.time()
        # check for new orders
        self.trucks.update(self.lemonade_stand, self.current_datetime, self.sound)
        self.clouds.update()

        # if it's the end of the day, recap, setup for tomorrow
        if not self.current_datetime.date() == old_datetime.date():
            outcomes, word_of_mouth_effect, self.daily_report = end_day(self)
            print(outcomes)
            self.word_of_mouth_effect = word_of_mouth_effect
            self.customer_outcomes = []
            self.customer_thoughts = []
            self.last_customer_thought = ''
            customers = self.get_starting_customers()
            track_day_start_stats(self)
            self.future_customers = pygame.sprite.Group(customers)
            self.active_customers.empty()
            self.customers_in_line.empty()
            self.customers_not_in_line.empty()
            self.lemonade_stand.lineup.clear()
            self.clouds.cloudiness = np.random.choice([0,0.2,0.4,0.6])


        # check for new customers arriving, add them to the update group
        for customer in self.future_customers.sprites():
            if customer.arrival_time < self.current_datetime.time():
                self.future_customers.remove(customer)
                self.active_customers.add(customer)
                self.customers_not_in_line.add(customer)
        self.lemonade_stand.update(self.current_datetime, game_speed_in_minutes, self.recipe)
        self.active_customers.update(game_speed_in_minutes, self.lemonade_stand.lineup,
                                     self.recipe, self.lemonade_stand.price, self.customer_outcomes, self.customer_thoughts, 
                                     self.customers_in_line, self.customers_not_in_line, self.sound)
        self.update_last_thought()

    def draw(self):
        self.screen.blit(self.background_sky.background, (0,0))
        self.clouds.clouds.draw(self.screen)
        self.town.draw(self.screen)
        self.trucks.draw(self.screen)
        self.trees.draw(self.screen)
        self.lemonade_stand.draw(self.current_datetime.time(),
                                    self.screen)
        self.customers_in_line.draw(self.screen)
        self.lemonade_stand.lineup.draw(self.screen)
        self.customers_not_in_line.draw(self.screen)
        # self.active_customers.draw(self.screen)

    def update_last_thought(self):
        if len(self.customer_thoughts) > 0:
            if self.last_thinking_customer != self.customer_thoughts[-1][0]:
                self.last_customer_thought = f'"{np.random.choice(self.customer_thoughts[-1][1])}"'
                self.last_thinking_customer = self.customer_thoughts[-1][0]
                self.thought_frames = 0
            else:
                self.thought_frames += 1

    def print_thought(self):
        font = pygame.font.Font(FONT_STYLE, 14)
        txt_color = (184, 178, 140)
        if self.thought_frames < 30:
            self.screen.blit(
                    font.render(self.last_customer_thought, 1, txt_color), 
                    [(self.screen.get_width()/2) - 6*len(self.last_customer_thought), 5]
                )



    def print_stats(self):
        font = pygame.font.Font(FONT_STYLE, 14)  # Edit fonts here
        txt_color = RGB_WHITE


        # time_stamp = font.render(
        #     '{datetimstr} ({temp_txt} Celcius)'.format(
        #         datetimstr=self.current_datetime.strftime('%Y-%m-%d %H:%M %p'),
        #         temp_txt=get_temperature(self.current_datetime)
        #     ), 1, txt_color)
        # current_price = font.render(str(self.lemonade_stand.price) + ' $ / CUP', 1, txt_color)

        margin = 42
        icon_size = 24
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
        stat_bar_bg_img_x = int(2.25*margin*len(stocks))
        # print (stat_bar_bg_img_x)
        self.screen.blit(pygame.transform.scale(stat_bar_bg_img, (stat_bar_bg_img_x, 65)), [10, 530])
        # draw icons
        for i, img in enumerate(icon_imgs):
            self.screen.blit(pygame.transform.scale(img, (icon_size, icon_size)),
                             [20 + (icon_size + margin) * i, 540])
        # draw values
        for i, stock in enumerate(stocks):
            self.screen.blit(
                font.render('%.0f' % stock.current_units, 1, txt_color),
                [20 + (icon_size + margin) * i, 565]
            )
            self.screen.blit(
                font.render('/%.0f' % stock.capacity, 1, txt_color),
                [20 + (icon_size + margin) * i, 578]
            )

        # draw money
        money = self.lemonade_stand.account_balance
        self.screen.blit(
            font.render('$ %.0f' % money, 1, RGB_GREEN if money > 0 else RGB_RED),
            [20 + (icon_size + margin) * len(stocks), 565]
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
                [20 + (icon_size + margin) * i, countdown_offset]
            )
            amount_of_next_order_string = ''
            will_fit = True
            if amount is not None:
                amount_of_next_order_string = '+ %.0f' % amount
                will_fit = (stock.current_units + amount) <= stock.capacity
            self.screen.blit(
                font.render(amount_of_next_order_string, 1, txt_color if will_fit else RGB_RED),
                [20 + (icon_size + margin) * i, countdown_offset - 20]
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

        # date
        # import ipdb; ipdb.set_trace()
        date_font = pygame.font.Font(FONT_STYLE, 12)
        weekday = ['MON', 'TUES', 'WED', 'THUR', 'FRI', 'SAT', 'SUN']
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY',' JUNE', 'JULY', 'AUG', 'SEPT', 'OCT', 'NOV', 'DEC']
        # date_str = weekday[self.current_datetime.weekday()]+'-'+\
        date_str = months[self.current_datetime.month]+'-'+str(self.current_datetime.day)
        self.screen.blit(date_font.render(date_str, 1, txt_color), [40,7])

        # clock
        self.analog_clock.draw(self.screen)
