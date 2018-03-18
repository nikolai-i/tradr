from config import Config
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
