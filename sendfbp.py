
import gevent
from gevent import monkey
monkey.patch_all()

import websocket
import json
import sys
import os
import pandas

def send_inport_message(graph, inport, data):
    p = {
        'event': 'data',
        'port': inport,
        'graph': graph,
        'payload': data,
    }
    m = {
        'protocol': 'runtime',
        'command': 'packet',
        'payload': p,
    }
    return m

def map_linear(val, inmin=0, inmax=1.0, outmin=0, outmax=1.0):
    return (val-inmin) * (outmax-outmin) / (inmax-inmin) + outmin

def wind_sequence(path):
    fields = ['time', 'timestamp', 'speed', 'direction', 'latitude', 'longitude']
    df = pandas.read_csv(path, header=None, names=fields, index_col=0, parse_dates=[0])
    
    timerange = df.index.max() - df.index.min()

    desiredtime = 10.0 # seconds
    timefactor = timerange
    
    start = df['timestamp'].min()
    end = df['timestamp'].max()
    events = []
    for data in df.itertuples():
        _, timestamp, speed = data[:3]
        t = map_linear(timestamp, start, end, 0, desiredtime)
        v = map_linear(speed, 2.0, 4.2, 0, 100)
        #print('t', timestamp, t, speed, v)
        events.append((t, v))
    return events

def main():
    events = wind_sequence('data/hywind-park.2018-01-05T18:34:26.128293.csv')

    ws = websocket.create_connection("ws://localhost:3569")

    graph = 'default/main'
    inport = 'interval'

    current_time = 0
    for event in events:
        time, value = event
        print('t', time, value)
        wait = time - current_time
        gevent.sleep(wait)
        current_time += wait
        m = json.dumps(send_inport_message(graph, inport, value))
        ws.send(m)

    #print("waiting response")
    #result =  ws.recv()

    ws.close()

if __name__ == '__main__':
    main()
