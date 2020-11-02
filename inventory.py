from __future__ import annotations

from datetime import time, datetime, date
from typing import List

import numpy as np


def get_discounted_value(initial_dt: datetime, current_dt: datetime, discount_per_day: float) -> float:
    """discount_factor = exp(-1 * days * discount_per_day)"""
    elapsed_days = (current_dt - initial_dt).seconds / 86400
    return float(np.exp(-1 * elapsed_days * discount_per_day))


class Order:
    def __init__(self, order_dt: datetime, delivery_dt: datetime, units: float):
        """Orders are paid for at order_time"""
        self.order_dt = order_dt
        if not (delivery_dt >= order_dt):
            raise ValueError('Check that delivery_time >= order_time')
        self.delivery_dt = delivery_dt
        if not (units >= 0):
            raise ValueError('Check that units >= 0')
        self.units = units

    def __str__(self) -> str:
        return 'Order made at: {} of amount: {} to be delivered at: {}'.format(
            self.order_dt, self.units, self.delivery_dt
        )

    def __lt__(self, other: Order) -> bool:
        """Allows for sorting of List[Order]"""
        return self.order_dt < other.order_dt

    def is_delivered(self, t: time) -> bool:
        return t >= self.delivery_dt


class Stock:
    def __init__(self, initial_amount: float, initial_dt: datetime, discount_per_day: float):
        self.pending_orders: List[Order] = []
        self.current_dt = initial_dt
        if not initial_amount >= 0:
            raise ValueError('Check initial_amount >= 0')
        self.current_units = initial_amount
        if not (discount_per_day >= 0):
            raise ValueError('Check discount_per_day >= 0')
        self.discount_per_day = discount_per_day

    def __str__(self) -> str:
        return 'Stock of {} as of: {} with pending orders:\n{}'.format(
            self.current_units, self.current_dt, '\n'.join(str(order) for order in self.pending_orders)
        )

    def add_order(self, order: Order) -> None:
        if not (order.order_dt >= self.current_dt):
            raise ValueError(
                'Check that order_time: {} >= current_time: {}'.format(order.order_dt, self.current_dt))
        self.pending_orders.append(order)

    def _update_noorders(self, t: datetime) -> None:
        self.current_units *= get_discounted_value(self.current_dt, t, self.discount_per_day)
        self.current_time = t

    def _update_orders(self, t: datetime) -> List[Order]:
        """Updates state at time t"""
        new_pending_orders = []
        delivered_orders = []
        for order in self.pending_orders:
            if order.is_delivered(t):
                delivered_orders.append(order)
            else:
                new_pending_orders.append(order)
        self.pending_orders = new_pending_orders
        delivered_orders = sorted(delivered_orders)
        for order in delivered_orders:
            self._update_noorders(order.delivery_dt)
            self.current_units += order.units
        self._update_noorders(t)
        return delivered_orders

    def update(self, t: datetime, withdrawunits: float = 0.) -> List[Order]:
        """Update state at time t and withdraws units. Return delivered orders since last update."""
        if not withdrawunits >= 0:
            raise ValueError('Check units >= 0')
        delivered_orders = self._update_orders(t)
        self.current_units -= withdrawunits
        return delivered_orders


if __name__ == '__main__':

    def get_dummy_datetime(t: time) -> datetime:
        return datetime.combine(datetime.now().date(), t)

    dt0 = get_dummy_datetime(time(0))
    maxhours = 5
    itemstock = Stock(10, dt0, 2)
    cashstock = Stock(9, dt0, 0)

    print ('Comitting orders...')
    new_orders = [ ]
    for h in range(maxhours):
        order = Order(dt0, get_dummy_datetime(time(h)), 1)
        order_cost = 1.
        itemstock.add_order(order)
        cashstock.update(dt0, withdrawunits=order_cost)
        print ('{}, Cost: {}, Balance Post: {}'.format(order, order_cost, cashstock.current_units))

    x = []
    yprior = []
    ypost = []
    for h in range(maxhours):
        for m in [0, 15, 30, 45]:
            timenow = get_dummy_datetime(time(h, m, 0))
            stockpriorupdate = itemstock.current_units
            deliveredorderssince = itemstock.update(timenow)
            stockpostupdate = itemstock.current_units
            x.append(timenow)
            yprior.append(stockpriorupdate)
            ypost.append(stockpostupdate)

    import matplotlib.pyplot as plt

    for order in new_orders:
        plt.axvline(order.delivery_dt, color='red', ls=':', label='order')
    plt.plot(x, yprior, label='prior')
    plt.plot(x, ypost, label='post')
    plt.legend()
    plt.show()
