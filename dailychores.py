import pygame
import datetime
import numpy as np
from entities.customer import Customer
from collections import Counter
from demand import demand_seasonality
from lineup import Lineup
from typing import List
from entities.customer import CustomerArrivalTimeGenerator, CustomerPreferenceGenerator


def predict_demand(dt: datetime.date, word_of_mouth_effect: float) -> int:
    return int(100 * demand_seasonality(dt) + word_of_mouth_effect)

def get_starting_customers(
        dt: datetime.date,
        word_of_mouth_effect: float,
        arrival_time_generator: CustomerArrivalTimeGenerator,
        preference_generator: CustomerPreferenceGenerator,
        lineup: Lineup
) -> List[Customer]:
    n_customers_today = predict_demand(dt=dt, word_of_mouth_effect=word_of_mouth_effect)
    customers =[Customer(position=(np.random.choice([-150,950]), 500 + np.random.randint(-25,25)),
                         arrival_time_generator=arrival_time_generator,
                         pref_generator=preference_generator,
                         lineup=lineup,
                         hold_for_n_frames = 5)
                for _ in range(n_customers_today)]
    return customers

def end_day(lemonade_game):
    outcomes = (Counter(lemonade_game.customer_outcomes))
    word_of_mouth_effect = outcomes['Satisfied Customer'] - outcomes['Bad Experience']

    # pay employees
    for employee in lemonade_game.lemonade_stand.employees:
        lemonade_game.lemonade_stand.account_balance -= employee.daily_wage
    return outcomes, word_of_mouth_effect
