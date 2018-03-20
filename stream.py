from config import Config
import datetime
import requests
import json

oanda = Config()

def get_stream(instruments, id=oanda.id, token=oanda.token):
    return requests.get(
            oanda.stream_url.format(id, instruments),
            headers={'Authorization': 'Bearer {}'.format(token)},
            stream=True)

def get_data(instrument):
    with get_stream(instrument) as response:
        for chunk in response.iter_lines():
            yield json.loads(chunk.decode('utf-8'))

def parse_time(time):
    return datetime.datetime.strptime(time[:-4], '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(hours=11)

def filter(stream):
    while True:
        flag = False
        time = datetime.datetime.now()
        try:
            data = next(stream)
            if not flag and data['type'] == 'HEARTBEAT' and parse_time(data['time']) > time:
                flag = True
            elif not flag:
                print('OUTDATED ', datetime.datetime.now(), data)
            if flag:
                yield data
        except Exception as e:
            print(e)

def ema(last, new, alpha=0.4):
    if last == None:
        return new
    else:
        return new * alpha + last * (1 - alpha)

def trade(data, data_shadow, bid_count, ask_count, last, position, cash, tolerance=2):
    new = next(data)
    new_shadow = next(data_shadow)
    if new['type'] == 'PRICE':
        new_bids = float(new['bids'][0]['price'])
        new_asks = float(new['asks'][0]['price'])
    """
        print("spread: ", new_asks - new_bids)
        ask_ma = ema(last[1], new_asks)
        bid_ma = ema(last[0], new_bids)
        if ask_ma < new_bids:
            bid_count += 1
            if bid_count > tolerance:
                print('sell at ', new_bids)
                cash += new_bids
                position -= 1
            # sell instrument at bid price
        else:
            bid_count = 0
        last[0] = bid_ma
        if bid_ma > new_asks:
            ask_count += 1
            if ask_count > tolerance:
                print('buy at ', new_asks)
                cash -= new_asks
                position += 1
           # buy instrument at ask price
        else:
            ask_count = 0
        last[1] = ask_ma
        print('Net position: {}, Net value: {}'.format(position, 1000 * (position * (new_asks + new_bids) / 2 + cash)))
        if last[0] == None:
            pass
        elif last[0] < new_bids:
            print("sell at ", new_bids)
            cash += new_bids
            position -= 1
        last[0] = new_bids
        if last[1] == None:
            pass
        elif last[1] > new_asks:
            print("buy at ", new_asks)
            cash -= new_asks
            position += 1
        last[1] = new_asks
    """
    if new_shadow['type'] == 'PRICE':
        new_shadow_bids = 1 / float(new_shadow['asks'][0]['price'])
        new_shadow_asks = 1 / float(new_shadow['bids'][0]['price'])
        print(new_shadow_bids / new_bids, "\t", new_shadow_asks / new_asks)
        if new_bids > new_shadow_asks:
            print("sell instrument 1 at ", new_bids)
            print("buy instrument 2 at ", new_shadow_asks)
            cash = cash + new_bids - new_shadow_asks
        if new_ask < new_shadow_bids:
            print("buy instrument 1 at ", new_asks)
            print("sell intrusment 2 at ", new_shadow_bids)
            cash = cash - new_asks + new_shadow_bids
        print("cash: ", cash)
    return [bid_count, ask_count, last, position, cash]

def main(curr1, curr2, tolerance=1):
    data = get_data("{}_{}".format(curr1, curr2))
    data_shadow = get_data("{}_{}".format(curr2, curr1))
    bid_count, ask_count, cash = 0, 0, 0
    last = [None, None]
    position = 0
    while True:
        [bid_count, ask_count, last, position, cash] = \
                trade(data, data_shadow, bid_count, ask_count, last, position, cash, tolerance)

if __name__ == '__main__':
    main('GBP', 'USD', 0)
