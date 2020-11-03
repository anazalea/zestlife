from __future__ import annotations

from datetime import time, datetime, timedelta
from typing import List
import heapq

import numpy as np



class Stock:
    def __init__(self, name: str, initial_amount: float, initial_dt: datetime, shelf_life: float, delivery_time: float):
        self.current_dt = initial_dt
        self.name = name
        if not initial_amount > 0:
            raise ValueError('Check initial_amount >= 0')
        if not (shelf_life > 0):
            raise ValueError('Check shelf_life > 0')
        self.shelf_life = 3600*shelf_life 
        # assume shelf life is given in hours!!
        expiry_dt = initial_dt + timedelta(seconds=self.shelf_life)
        self.inventory = [(initial_dt, expiry_dt, [initial_amount])]
        self.delivery_time = 3600*delivery_time
            
    def count_inventory(self, t: datetime) -> int:
        res = 0
        print('\nInventory summary for {} as of {}'.format(
            self.name, t.strftime('%Y-%m-%d %H:%M:%S')))
        for x in self.inventory:
            dt1, dt2, amount = x[0], x[1], x[2][0]
            s1 = ''
            if dt1 <= t and t < dt2:
                res += amount
                print('  Amount {} with expiry date {}'.format(
                    amount, dt2.strftime('%Y-%m-%d %H:%M:%S')))
            elif t < dt1:
                print('  Amount {} to be delivered by {}'.format(
                    amount, dt1.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                print('  Amount {} has expired on {}'.format(
                    amount, dt2.strftime('%Y-%m-%d %H:%M:%S')))
                
        print('  Total usable amount: ', res, '\n')
        return res

    def add_order(self, t: datetime, units: float) -> None:
        if not (units > 0):
            raise ValueError('Units can not be zero')
        delivery_dt = t + timedelta(seconds=self.delivery_time)
        expiry_dt = delivery_dt + timedelta(seconds=self.shelf_life)
        heapq.heappush(self.inventory, (delivery_dt, expiry_dt, [units]))
        self.count_inventory(t)


    def update(self, t: datetime, withdrawunits: float = 0.) -> int:
        """Update state at time t and withdraws units. Return True if inventory has more items"""
        if not withdrawunits >= 0:
            raise ValueError('Check units >= 0')
        count = withdrawunits
        while count > 0.0 and len(self.inventory) > 0:
            x = self.inventory[0]
            dt1, dt2, amount = x[0], x[1], x[2][0]
            if dt1 > t: # no delivered orders exist!
                break
            if t < dt2: # if items haven't expired yet
                decrease = min(count, amount)
                count -= decrease
                amount -= decrease
            self.inventory[0][2][0] = amount
            if t >= dt2 or amount == 0: # if the items have expired and/or no items are left
                heapq.heappop(self.inventory)
        print('Consumed {} {} out of {} units required at {}'.format(
            withdrawunits-count, self.name, withdrawunits, t))
        self.count_inventory(t)
        return count # if > 0 than it means we don't have enough inventory, maybe raise stock-out error?


if __name__ == '__main__':

    t = datetime.today()

    lemons = Stock('Lemons', 10.0, t, 4.0, 1.0)
    sugar = Stock('Sugar', 130.0, t, 100000.0, 2.0) # has basically infinite shelf-life

    t += timedelta(hours=2)
    lemons.update(t, 4)
    sugar.update(t, 89)

    t += timedelta(hours=3)
    lemons.add_order(t, 15)
    sugar.add_order(t, 120)

    t += timedelta(hours=3)
    lemons.update(t, 3)
    sugar.update(t, 300)



