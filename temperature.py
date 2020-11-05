from datetime import date

FLOTEMPS = {
    1: 10.7,
    2: 12.6,
    3: 15.8,
    4: 18.9,
    5: 23.5,
    6: 26.8,
    7: 27.8,
    8: 27.7,
    9: 25.7,
    10: 20.8,
    11: 15.7,
    12: 11.8
}


def get_temperature(dt: date) -> float:
    return FLOTEMPS[dt.month] if dt.month in FLOTEMPS else 10.


if __name__ == '__main__':
    from datetime import timedelta
    import matplotlib.pyplot as plt

    dates = [date(2000, 1, 1) + timedelta(days=d) for d in range(720)]
    plt.plot(dates, [get_temperature(dt) for dt in dates])
    plt.show()
