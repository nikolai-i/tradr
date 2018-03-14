"""Logistic Model
    This model intends to use the closing price of previous period
    as predictor, if the possibility of the prediction exceeds
    #alpha percent, flag the situtation as tradable."""

import numpy as np

""" I will review whether it is viable to run stochastic gradient
    descent logistic regression on stock market.
"""

def logi(theta, last):
    return 1 / (1 + np.exp(-theta[0] - theta[1] * last))

def bot(exchange, alpha=0.3, theta=[0, 0]):
    last = next(exchange).Close
    for info in exchange:
        temp = next(exchange).Close
        flag = np.sign(temp / last - 1) / 2 + 0.5
        theta = [
                theta[0] + alpha * (flag - logi(theta, temp)),
                theta[1] + alpha * (flag - logi(theta, temp) * temp)]
        last = temp
        proj = logi(theta, last)
        if proj > 0.8:
            yield 1
        elif proj < 0.2:
            yield -1
        else:
            yield 0
