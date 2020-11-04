import pygame
import numpy as np

class Spot():
    def __init__(self, loc):
        self.loc = loc
        self.is_occupied = False
        self.occupant = None

class Lineup():
    def __init__(self, loc_first, loc_last, n_positions):
        self.spots = {}
        self.n_spots = n_positions
        self.n_positions = n_positions
        self.last_loc = loc_last
        xlocs = np.linspace(loc_first[0], loc_last[0], n_positions)
        ylocs = np.linspace(loc_first[1], loc_last[1], n_positions)
        for i in range(n_positions):
            self.spots[i] = Spot(loc = (int(xlocs[i]),int(ylocs[i])))

    def clear(self):
        for i in range(self.n_positions):
            self.spots[i].is_occupied = False
            self.spots[i].occupant = None
        



