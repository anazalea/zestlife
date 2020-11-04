import pygame
import datetime
import numpy as np
from entities.customer import Customer
from collections import Counter
from demand import demand_seasonality

def predict_demand(date, word_of_mouth_effect):
    return 50 * demand_seasonality(date) + word_of_mouth_effect

def start_day(lemonade_game):
    # update weather

    # calculate demand
    n_customers_today = predict_demand(lemonade_game.current_datetime.date(),
                                        lemonade_game.word_of_mouth_effect)

    # generate customers
    customers =[Customer((np.random.choice([-150,950]), 300 + np.random.randint(-25,25)), 
                        lemonade_game.arrival_time_generator, 
                        lemonade_game.preference_generator,
                        lemonade_game.customer_image_dict,
                        lemonade_game.lemonade_stand.lineup,
                        hold_for_n_frames=10) for i in range(n_customers_today)]

    return customers

def end_day(lemonade_game):
    outcomes = (Counter(lemonade_game.customer_outcomes))
    word_of_mouth_effect = outcomes['Satisfied Customer'] - outcomes['Bad Experience']
    return outcomes, word_of_mouth_effect
