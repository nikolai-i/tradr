import pandas as pd
import numpy as np
import json
import requests
import datetime
import itertools

portfolio = {"AAPL": 0, "BOND": 0, "MSFT": 0}

def get_history(symb):
    request_url = "https://www.google.com/finance/getprices?i=60&p=15d&f=d,o,h,l,c,v&df=cpct&q=" + symb
    data = requests.get(request_url).content.decode("utf-8", "ignore").split("\n")
    parsed = []
    anchor = datetime.datetime.now()
    for i in range(7, len(data) - 1):
        quote = data[i].split(",")
        if quote[0].startswith("a"):
            anchor = datetime.datetime.fromtimestamp(int(quote[0][1:]))
            cts = anchor
        elif quote[0].startswith("TIMEZONE"):
            continue
        else:
            cts = anchor + datetime.timedelta(0, 60)
        parsed.append((cts,
                       float(quote[1]),
                       float(quote[2]),
                       float(quote[3]),
                       float(quote[4]),
                       float(quote[5])))
    result = pd.DataFrame(parsed)
    result.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    result.index = result.Time
    del result["Time"]
    return result

AAPL = get_history("AAPL")
GOOG = get_history("GOOG")
MSFT = get_history("MSFT")

def market():
    yield '{"type": "hello"}'
    for i in range(len(AAPL.index)):
        yield '{"type": "fill", "symb": "AAPL", "dir" : "BUY", "info": %s}' % AAPL.iloc[i][1]
        yield '{"type": "fill", "symb": "AAPL", "dir" : "SELL", "info": %s}' % AAPL.iloc[i][2]
        yield '{"type": "fill", "symb": "GOOG", "dir" : "BUY", "info": %s}' % GOOG.iloc[i][1]
        yield '{"type": "fill", "symb": "GOOG", "dir" : "SELL", "info": %s}' % GOOG.iloc[i][2]
        yield '{"type": "fill", "symb": "MSFT", "dir" : "BUY", "info": %s}' % MSFT.iloc[i][1]
        yield '{"type": "fill", "symb": "MSFT", "dir" : "SELL", "info": %s}' % MSFT.iloc[i][2]

mart = market()

class Exchange:
    def __init__(self):
        hello_exchange = self.read()
        assert hello_exchange["type"] == "hello"
        self.order_id = 0

    def read(self):
        try:
            data = next(mart)
            data = json.loads(data)
            self.last_data = data
        except StopIteration:
            return None
