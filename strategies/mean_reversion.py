"""Mean Reversion Strategy
    This strategy compares the exponential moving average
    of the closing PRICE, if the price stays beyond EMA(n)
    for #k days, the strategy will recommend sell the
    asset and vice versa."""

import numpy as np

def ema(alpha, new, last=None):
    if last == None:
        return new
    else:
        return alpha * new + (1 - alpha) * last

def bot(exchange, alpha=0.3, days=5):
    last = None
    count, diff = 0, 0
    for info in exchange:
        last = ema(alpha, info.Close, last)
        if diff * (last - info.Close) > 0:
            count += 1
        else:
            count = 0
        diff = last - info.Close
        if count >= days:
            yield int(np.sign(diff))
        else:
            yield 0
