from __future__ import annotations

from datetime import time, datetime
from typing import List, Optional, Tuple

import numpy as np


def get_discounted_value(initial_dt: datetime, current_dt: datetime, discount_per_day: float) -> float:
    """discount_factor = exp(-1 * days * discount_per_day)"""
    elapsed_days = (current_dt - initial_dt).seconds / 86400
    return float(np.exp(-1 * elapsed_days * discount_per_day))


class NegativeStockError(Exception):
    pass


class NoTimeTravelError(Exception):
    pass


class Order:
    """Orders are paid for at order_dt with amount to be delivered at delivery_dt.
    """

    def __init__(self, order_dt: datetime, delivery_dt: datetime, amount: float):
        self.order_dt = order_dt
        if not (delivery_dt >= order_dt):
            raise ValueError('Check that delivery_time >= order_time')
        self.delivery_dt = delivery_dt
        if not (amount >= 0):
            raise ValueError('Check that amount >= 0')
        self.amount = amount

    def __str__(self) -> str:
        return 'Order of: {} made at: {} to be delivered at: {}'.format(
            '%.2f' % self.amount, self.order_dt, self.delivery_dt
        )

    def __lt__(self, other: Order) -> bool:
        """Allows for sorting of List[Order]"""
        return self.order_dt < other.order_dt

    def is_delivered(self, t: time) -> bool:
        return t >= self.delivery_dt


class ShrinkEvent:
    """Shrink of amount occured at dt due to reason.
    """

    def __init__(self, dt: datetime, amount: float, reason: str = ''):
        self.dt = dt
        if not amount >= 0:
            raise ValueError('Check amount: {} >= 0'.format(amount))
        self.amount = amount
        self.reason = reason

    def __str__(self):
        return 'Shrink of: {} at {} due to {}'.format(
            '%.4f' % self.amount, self.dt, self.reason
        )


class Stock:
    """Stock is updated by degradation, delivery of orders and withdraws.
    Raises NegativeStockError if withdraw results in negative stock if raise_error_if_neg.

    Methods:
        self.add_order(Order) adds new order.
        self.update(t, withdraw, new_capacity) returns current_units, delivered_orders since previous update.
    """

    def __init__(
            self,
            initial_amount: float, initial_dt: datetime,
            discount_per_day: float = 0.,
            capacity: Optional[float] = None,
            raise_error_if_neg: bool = True
    ):
        self.pending_orders: List[Order] = []
        self.shrink_log: List[ShrinkEvent] = []
        self.capacity = capacity
        self.raise_error_if_neg = raise_error_if_neg
        # initial_amount
        if not initial_amount >= 0:
            raise ValueError('Check initial_amount >= 0')
        if self.capacity is not None and not initial_amount <= capacity:
            raise ValueError('Check initial_amount <= capacity')
        self.current_units = initial_amount
        # initial_dt
        self.current_dt = initial_dt
        # discount_per_day
        if not (discount_per_day >= 0):
            raise ValueError('Check discount_per_day >= 0')
        self.discount_per_day = discount_per_day

    def __str__(self) -> str:
        return 'Stock of {} as of: {} with pending orders:\n{}'.format(
            '%.4f' % self.current_units, self.current_dt, '\n'.join(str(order) for order in self.pending_orders)
        )

    def _check_no_time_travel(self, t: datetime):
        if not t >= self.current_dt:
            raise NoTimeTravelError()

    def add_order(self, order: Order) -> None:
        self._check_no_time_travel(order.order_dt)
        self.pending_orders.append(order)

    def _check_capacity_bounds(self, new_units: float) -> float:
        if new_units < 0:
            if self.raise_error_if_neg:
                raise NegativeStockError()
        if self.capacity is not None and new_units > self.capacity:
            return self.capacity
        return new_units

    def _update_degradation(self, t: datetime) -> None:
        """Updates state at time t accounting only for degradation since last update"""
        new_current_units = self.current_units * get_discounted_value(self.current_dt, t, self.discount_per_day)
        new_current_units = self._check_capacity_bounds(new_current_units)  # shouldn't raise error.
        degraded_units = self.current_units - new_current_units
        self.shrink_log.append(ShrinkEvent(dt=t, amount=degraded_units, reason='Degradation'))
        self.current_units -= degraded_units
        self.current_dt = t

    def _update_orders(self, t: datetime) -> Tuple[float, List[Order]]:
        """Updates state at time t accounting for orders and degradation since last update"""
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
            self._update_degradation(order.delivery_dt)
            # possible over-capacity event here.
            candidate_units = self.current_units + order.amount
            new_current_units = self._check_capacity_bounds(candidate_units)
            wastage = candidate_units - new_current_units
            if wastage > 0:
                self.shrink_log.append(
                    ShrinkEvent(dt=order.delivery_dt, amount=wastage, reason='Over-Capacity')
                )
            self.current_units = new_current_units
        self._update_degradation(t)
        return self.current_units, delivered_orders

    def update(self, t: datetime, withdraw: float = 0., new_capacity: Optional[float] = None) -> Tuple[
        float, List[Order]]:
        """Update state at time t and withdraws units. Return delivered orders since last update."""
        self._check_no_time_travel(t)
        _, delivered_orders = self._update_orders(t)
        self.current_units -= withdraw
        if new_capacity is not None:
            self.capacity = new_capacity
            new_units = self._check_capacity_bounds(self.current_units)
            if new_units < self.current_units:
                wastage = self.current_units - new_units
                self.shrink_log.append(
                    ShrinkEvent(dt=t, amount=wastage, reason='Decreased-Capacity')
                )
            self.current_units = new_units
        return self.current_units, delivered_orders


if __name__ == '__main__':
    import matplotlib.pyplot as plt


    def get_dummy_datetime(t: time) -> datetime:
        return datetime.combine(datetime.now().date(), t)


    # set some parameters
    maxh = 10
    hourlyconsumption = 2
    lemoncapacity = 20.
    newcapacity = 10.
    dt0 = get_dummy_datetime(time(0))
    initialstock = 10.

    # initialize lemon, cash inventory
    lemonstock = Stock()
    cashstock = Stock(initial_amount=100., initial_dt=dt0, discount_per_day=0., raise_error_if_neg=False)

    print('\nComitting orders...')
    lemonorders = []
    for h, v in zip([1, 2, 5, 8], [5, 15, 5, 5]):
        lemonorder = Order(order_dt=dt0, delivery_dt=get_dummy_datetime(time(h)), amount=v)
        lemonordercost = v / 2
        lemonorders.append(lemonorder)
        lemonstock.add_order(lemonorder)
        balance_prior = cashstock.current_units
        cashstock.update(dt0, withdraw=lemonordercost)
        print('{}, Balance: {} -> {}'.format(lemonorder, balance_prior, cashstock.current_units))

    print('\nSimulating stock...')
    x = []
    y = []
    totalconsumption = 0
    for h in range(maxh):
        for m in range(60):
            timenow = get_dummy_datetime(time(h, m, 0))
            # consumption
            consumption = hourlyconsumption / 60
            totalconsumption += consumption
            if h == 5 and m == 30:
                units, deliveredorderssince = lemonstock.update(timenow, withdraw=consumption, new_capacity=newcapacity)
            else:
                units, deliveredorderssince = lemonstock.update(timenow, withdraw=consumption)
            # accumulate some information regarding post updat state
            x.append(timenow)
            y.append(units)
            print('timenow: {}, units: {}, #orders: {}'.format(
                timenow, '%.2f' % units, len(deliveredorderssince)
            ))

    print('\n'.join(str(i) for i in lemonstock.shrink_log))

    # visual test
    totalordered = sum(i.amount for i in lemonorders)
    totalshrink = sum(i.amount for i in lemonstock.shrink_log)
    print('initialstock: {}, totalconsumption: {}, totalordered: {}, totalshrink: {}, finalstock: {}'.format(
        initialstock, totalconsumption, totalordered, totalshrink, lemonstock.current_units
    ))
    # the one test
    print('initialstock - totalconsumption + totalordered - totalshrink = finalstock?: {}'.format(
        np.abs(initialstock - totalconsumption + totalordered - totalshrink - lemonstock.current_units) < 1e-3
    ))

    # another visual test
    plt.plot(x, y, label='units')
    plt.axhline(lemoncapacity, color='blue', ls=':', label='lemoncapacity')
    plt.axhline(newcapacity, color='blue', ls=':', label='newcapacity')
    for order in lemonorders:
        plt.axvline(order.delivery_dt, color='red', ls=':', label='order amount: {}'.format(order.amount))
    for shrinkevent in lemonstock.shrink_log:
        if shrinkevent.reason == 'Over-Capacity':
            plt.scatter(shrinkevent.dt, lemoncapacity, label='Over-Capacity', color='red', s=25, marker='x')
        if shrinkevent.reason == 'Decreased-Capacity':
            plt.scatter(shrinkevent.dt, newcapacity, label='Decreased-Capacity', color='orange', s=25, marker='x')
    plt.title('lemonstock')
    plt.legend()
    plt.show()
