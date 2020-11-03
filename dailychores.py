import pygame
import datetime
import numpy as np
from entities.customer import Customer

def predict_demand(date):
    return 10

def start_day(lemonade_game):
    # update weather

    # calculate demand
    n_customers_today = predict_demand(lemonade_game.current_datetime.date())

    # generate customers
    customers =[Customer((0, 300 + np.random.randint(-25,25)), 
                        lemonade_game.arrival_time_generator, 
                        lemonade_game.preference_generator,
                        lemonade_game.customer_image_dict,
                        hold_for_n_frames=10) for i in range(n_customers_today)]

    return customers

def end_day():
    pass
