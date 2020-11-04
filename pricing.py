from datetime import timedelta

import numpy as np

SECSIND = 86400


def get_discountedprice(
        lead_time: timedelta, amount: float = 0.,
        bulk_discount_unitly: float = 0., lead_discount_daily: float = 0.,
        base_price: float = 1., min_price: float = 0.
) -> float:
    if not amount >= 0:
        raise ValueError('check amount >= 0')
    lead_days = lead_time.total_seconds() / SECSIND
    discount_lead = float(np.exp(-1. * lead_days * lead_discount_daily))
    discount_bulk = float(np.exp(-1. * max(0, amount - 1) * bulk_discount_unitly))
    discount_interaction = min(discount_lead, discount_bulk) / .5 * (discount_lead + discount_bulk)  # ayyy
    unit_price = base_price * discount_bulk * discount_lead * discount_interaction
    return max(unit_price, min_price)


def get_lemon_discountedprice(lead_time: timedelta, amount: float = 0.) -> float:
    return get_discountedprice(
        lead_time, amount,
        bulk_discount_unitly=.01, lead_discount_daily=1.,
        base_price=1., min_price=0.5,
    )

def get_sugar_discountedprice(lead_time: timedelta, amount: float = 0.) -> float:
    return get_discountedprice(
        lead_time, amount,
        bulk_discount_unitly=.02, lead_discount_daily=.2, # sugar is bulky, doesn't degrate
        base_price=1., min_price=0.5,
    )

def get_ice_discountedprice(lead_time: timedelta, amount: float = 0.) -> float:
    return get_discountedprice(
        lead_time, amount,
        bulk_discount_unitly=.03, lead_discount_daily=.2, # ice is very bulky, doesn't degrade
        base_price=1., min_price=0.5,
    )


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    n = 100
    lead_hours = np.linspace(0, 24, n)
    for amount in range(0, 10, 2):
        plt.plot(lead_hours, [get_lemon_discountedprice(timedelta(hours=h), amount) for h in lead_hours])
        plt.title('amount: {}'.format(amount))
        plt.show()
