import pygame
import datetime
from datetime import timedelta
import numpy as np
from entities.employee import Employee
from entities.coin import Coin, coin_im_dict
from lineup import Lineup
from recipe import Recipe
from inventory import Stock
from enum import Enum

LEMON_INISTOCK = 500
SUGAR_INISTOCK = 500
ICE_INISTOCK = 500
CASH_INI = 1000

class StandType(Enum):
    A = 'A'
    B = 'B'
    C = 'C'

class StandTypeConfig:
    image = pygame.image.load('./resources/standA_small.png')
    juicing_efficiency = 45
    lemon_capacity = 500
    sugar_capacity = 500
    ice_capacity = 500

class StandTypeConfigB(StandTypeConfig):
    image = pygame.image.load('./resources/standB_small.png')
    juicing_efficiency = 55
    lemon_capacity = 1000
    sugar_capacity = 1000
    ice_capacity = 1000

class StandTypeConfigC(StandTypeConfig):
    image = pygame.image.load('./resources/standC_small.png')
    juicing_efficiency = 75
    lemon_capacity = 2000
    sugar_capacity = 2000
    ice_capacity = 2000

def get_stand_config(stand_type: StandType) -> StandTypeConfig:
    if stand_type == StandType.A:
        return StandTypeConfig
    elif stand_type == StandType.B:
        return StandTypeConfigB
    elif stand_type == StandType.C:
        return StandTypeConfigC
    return StandTypeConfig

UPGRADE_COST = 500
DOWNGRADE_REFUND = 400
STAND_TYPE_ORDERING = [StandType.A, StandType.B, StandType.C]

def get_stand_upgrade(current_stand_type: StandType) -> StandType:
    new_index = STAND_TYPE_ORDERING.index(current_stand_type) + 1
    try:
        return STAND_TYPE_ORDERING[new_index]
    except IndexError:
        pass
    return current_stand_type

def get_stand_downgrade(current_stand_type: StandType) -> StandType:
    new_index = STAND_TYPE_ORDERING.index(current_stand_type) - 1
    if new_index >= 0:
        return STAND_TYPE_ORDERING[new_index]
    return current_stand_type


class LemonadeStand():
    def __init__(self, screen, current_datetime, employee_image_dict, sound, n_employees=3, stand_type: StandType = StandType.A):
        self.stand_type: StandType = stand_type
        self.lemonstock: Stock = Stock(
            initial_amount=LEMON_INISTOCK, initial_dt=current_datetime,
            discount_per_day=0.01, capacity=LEMON_INISTOCK
        )
        self.sugarstock: Stock = Stock(
            initial_amount=SUGAR_INISTOCK, initial_dt=current_datetime,
            discount_per_day=0.001, capacity=SUGAR_INISTOCK
        ) # g
        self.icestock: Stock = Stock(
            initial_amount=ICE_INISTOCK, initial_dt=current_datetime,
            discount_per_day=0.5, capacity=ICE_INISTOCK
        )
        # this guy updates a bunch of adjustables depending on stand_type
        self.refresh_lemonade_stand_with_new_type(dt=current_datetime, stand_type=stand_type)
        # independent of stand_type
        self.im_height = self.image_open.get_height()
        self.im_width = self.image_open.get_width()
        self.loc = [250,325]
        self.sound = sound
        self.opening_time = datetime.time(8)
        self.closing_time = datetime.time(20)
        self.open = True
        self.open = self.is_open(current_datetime.time())
        self.account_balance = CASH_INI # $
        self.price = 2.00
        self.lineup = Lineup((300,400),(700,400) ,10)
        self.prep_time = 45 # minutes/lemonade, should depend on number of employees
        self.time_serving_customer = 0
        self.recent_customer_thought = ''
        self.employees = []
        self.outstanding_wages = 0
        self.workforce = pygame.sprite.Group(self.employees)
        self.employee_image_dict = employee_image_dict
        self.coin_group = pygame.sprite.Group([])
        self.lemonade_stand_level = 0
        self.n_customers_served = 0

        for i in range(n_employees):
            self.hire_employee(self.opening_time, self.closing_time, self.employee_image_dict,current_datetime.time(),daily_wage=(i+2)*10)

    def refresh_lemonade_stand_with_new_type(self, dt: datetime.datetime, stand_type: StandType):
        self.stand_type = stand_type
        new_config: StandTypeConfig = get_stand_config(stand_type)
        self.image_open = new_config.image
        self.image_closed = new_config.image
        # juicing_efficiency
        self.juicing_efficiency = new_config.juicing_efficiency
        # stock capacities
        self.lemonstock.update(t=dt, new_capacity=new_config.lemon_capacity)
        self.sugarstock.update(t=dt, new_capacity=new_config.sugar_capacity)
        self.icestock.update(t=dt, new_capacity=new_config.ice_capacity)

    def upgrade_stand(self, dt: datetime.datetime):
        new_stand_type = get_stand_upgrade(self.stand_type)
        will_change_type = new_stand_type != self.stand_type
        self.refresh_lemonade_stand_with_new_type(dt=dt, stand_type=new_stand_type)
        if will_change_type:
            self.account_balance -= UPGRADE_COST

    def downgrade_stand(self, dt: datetime.datetime):
        new_stand_type = get_stand_downgrade(self.stand_type)
        will_change_type = new_stand_type != self.stand_type
        self.refresh_lemonade_stand_with_new_type(dt=dt, stand_type=new_stand_type)
        if will_change_type:
            self.account_balance += DOWNGRADE_REFUND

    def update_prep_time(self):
        if len(self.employees) == 0:
            self.prep_time = np.inf
        else:
            self.prep_time = 3 * (len(self.employees) - 5) ** 2 + 5

    def hire_employee(self, start_time, end_time, employee_image_dict, current_time, daily_wage=20):
        # currently, employees should go in here: (270,350,90,50)
        new_employee = Employee((250,350), employee_image_dict, self.opening_time, self.closing_time, daily_wage=daily_wage)
        new_employee.clock_in(current_time)
        self.employees.append(new_employee)
        # reposition existing employees
        employee_locs = np.linspace(260, 260+90, len(self.employees)+2)
        states = list(employee_image_dict.keys())

        for i, employee in enumerate(self.employees):
            employee.state = states[i%len(states)]
            if employee.state == 'watch':
                employee.hold_for_n_frames = 40
            employee.rect[:2] = [employee_locs[i+1],360 + np.random.randint(-2,5)]
            employee.index = 0
        self.workforce = pygame.sprite.Group(self.employees)
        self.update_prep_time()

    def fire_employee(self, employee_image_dict, current_time, daily_wage):
        #Find an employee with the right wage
        for i in range(len(self.employees)):
            if self.employees[i].daily_wage == daily_wage:
                self.employees[i].clock_out(current_time)
                self.outstanding_wages += self.employees[i].get_owed_wages()
                self.employees.pop(i)
                break
        #reposition existing employees
        employee_locs = np.linspace(260, 260+90, len(self.employees)+2)
        states = list(employee_image_dict.keys())
        last_state = states[0]
        for i, employee in enumerate(self.employees):
            if employee.state == last_state:
                employee.state = states[(states.index(employee.state)+1)%len(states)]
            employee.rect[:2] = [employee_locs[i+1],362 + np.random.randint(-5,5)]
            employee.index = np.random.choice([0,1,2])
            last_state = employee.state
        self.workforce = pygame.sprite.Group(self.employees)
        self.update_prep_time()

    def get_current_employees(self):
        return self.employees

    def is_open(self, current_time):
        if not self.open and self.opening_time < current_time < self.closing_time:
            self.sound.play_sfx(self.sound.powerup_appear)
        return self.opening_time < current_time < self.closing_time

    def make_a_sale(self, dt: datetime, recipe: Recipe):
        self.n_customers_served += 1
        _, _ = self.lemonstock.update(t=dt, withdraw=recipe.lemon_juice / self.juicing_efficiency)
        _, _ = self.icestock.update(t=dt, withdraw=recipe.ice)
        _, _ = self.sugarstock.update(t=dt, withdraw=recipe.sugar)
        self.account_balance += self.price

    def serve_customer(self, recipe: Recipe, current_datetime: datetime, tdelta_minutes: float):
        """Processes lineup and makes sale between current_datetime and current_datetime+deltat"""
        if not self.lineup.spots[0].is_occupied:
            # nothing happens
            return None
        if not self.has_enough_stuff(recipe) or not self.open:
            # go home
            self.lineup.spots[0].occupant.likes_recipe = False
            self.time_serving_customer = 0
        if all([
            self.lineup.spots[0].occupant.likes_recipe,
            not self.lineup.spots[0].occupant.has_lemonade,
            self.open,
            self.has_enough_stuff(recipe),
        ]):
            # will_have_sale
            self.time_serving_customer += tdelta_minutes
            if self.time_serving_customer > self.prep_time:
                self.lineup.spots[0].occupant.has_lemonade = True
                self.coin_group.add(Coin((300+np.random.randint(-10,10),305), image_dict=coin_im_dict))
                self.sound.play_sfx(self.sound.coin)
                self.time_serving_customer = 0
                self.make_a_sale(dt=current_datetime+timedelta(minutes=.5*tdelta_minutes), recipe=recipe)


    def update(self, current_datetime: datetime, tdelta_minutes: float, recipe: Recipe):
        """Updates state to next state from current_datetime to current_datetime to timedelta."""
        self.open = self.is_open(current_datetime.time())
        _, _ = self.lemonstock.update(current_datetime)
        _, _ = self.sugarstock.update(current_datetime)
        _, _ = self.icestock.update(current_datetime)
        self.serve_customer(recipe=recipe, current_datetime=current_datetime, tdelta_minutes=tdelta_minutes)
        self.coin_group.update()

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
            self.workforce.draw(screen)
            screen.blit(self.image_open, self.loc)
        else:
            screen.blit(self.image_closed, self.loc)
        self.coin_group.draw(screen)

    def has_enough_stuff(self, recipe):
        if self.lemonstock.current_units * self.juicing_efficiency < recipe.lemon_juice:
            return False
        if self.sugarstock.current_units < recipe.sugar:
            return False
        if self.icestock.current_units < recipe.ice:
            return False
        else:
            return True
