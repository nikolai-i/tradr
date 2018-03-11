import numpy as np
import pandas as pd

def exchange(tickr):
    history = pd.read_csv('{}.csv'.format(tickr))
    history.index = history['Date']
    newcol = list(history.columns)
    newcol.remove('Date')
    newcol.remove('Volume')
    for _, row in history[newcol].iterrows():
        yield row
