import pygame
import datetime
import numpy as np
from entities.customer import Customer
from collections import Counter
from demand import demand_seasonality
from lineup import Lineup
from typing import List
from entities.customer import CustomerArrivalTimeGenerator, CustomerType


def predict_demand(dt: datetime.date, word_of_mouth_effect: float) -> int:
    return int(100 * demand_seasonality(dt) + word_of_mouth_effect)

def get_starting_customers(
        dt: datetime.date,
        word_of_mouth_effect: float,
        arrival_time_generator: CustomerArrivalTimeGenerator,
        customer_karen_prob: float,
        customer_hipster_prob: float,
        lineup: Lineup
) -> List[Customer]:
    default_prob = 1 - customer_hipster_prob - customer_karen_prob
    customers = []
    for _ in range(predict_demand(dt=dt, word_of_mouth_effect=word_of_mouth_effect)):
        customer_type = np.random.choice(
            [CustomerType.default, CustomerType.hipster, CustomerType.karen],
            p=[default_prob, customer_hipster_prob, customer_karen_prob]
        )
        customers.append(Customer(position=(np.random.choice([-150,950]), 500 + np.random.randint(-25,25)),
                         arrival_time_generator=arrival_time_generator,
                         customer_type=customer_type,
                         lineup=lineup,
                         hold_for_n_frames = 5))
    return customers

def track_day_start_stats(lemonade_game):
    # TODO: not nice! this is monkey patching
    ls = lemonade_game.lemonade_stand
    ls._day_start_sugar = ls.sugarstock.current_units
    ls._day_start_lemon = ls.lemonstock.current_units
    ls._day_start_ice = ls.icestock.current_units
    ls._day_start_acc_balance = ls.account_balance


yesterday_suger = 0

def end_day(lemonade_game):
    # TODO: don't take the entire lemonade_game object. Await merge of https://github.com/anazalea/lemonade/pull/23/files
    outcomes = (Counter(lemonade_game.customer_outcomes))
    word_of_mouth_effect = outcomes['Satisfied Customer'] - outcomes['Bad Experience']

    # pay employees
    total_wage = sum(e.daily_wage for e in lemonade_game.lemonade_stand.employees)
    lemonade_game.lemonade_stand.account_balance -= total_wage
    lemonade_game.lemonade_stand


    ls = lemonade_game.lemonade_stand

    daily_report = [
        f"Customers:                          {sum(outcomes.values())}",
        f"    Left because line was too long: {outcomes['Line Too Long']}",
        f"    Bad Experience:                 {outcomes['Bad Experience']}",
        f"    Satisfied Customer:             {outcomes['Satisfied Customer']}",
        "",
        f"Change in inventory:",
        f"    lemon: {ls.lemonstock.current_units - ls._day_start_lemon:.2f}",
        f"    sugar: {ls.sugarstock.current_units - ls._day_start_sugar:.2f}",
        f"    ice cube: {ls.icestock.current_units - ls._day_start_ice:.2f}",
        "",
        f"Current inventory:",
        f"    lemon: {ls.lemonstock.current_units:.2f}",
        f"    sugar: {ls.sugarstock.current_units:.2f}",
        f"    ice cube: {ls.icestock.current_units:.2f}",
        "",
        f"Wages deduced: ${total_wage:.2f}",
        "",
        f"revenue: ${ls.account_balance - ls._day_start_acc_balance:.2f}",
    ]
    return outcomes, word_of_mouth_effect, daily_report
