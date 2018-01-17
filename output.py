
import gevent
from gevent import monkey
monkey.patch_all()

import websocket
import json
import sys
import os
import pandas


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
        v = map_linear(speed, 0.0, 15.0, 0, 1024)
        #print('t', timestamp, t, speed, v)
        events.append((t, v))
    return events

def gen_c(vals, name='wind_data', ctype='uint16_t'):
    numbers = [ str(int(v)) for v in vals ]
    r = "static const {} {}[] = {{ {} }};".format(ctype, name, ','.join(numbers))
    return r

def main():
    events = wind_sequence('data/hywind-park.2018-01-05T18:34:26.128293.csv')

    vals = [ v for t,v in events ]
    t = gen_c(vals, name='speeds')
    filename = 'data.h'
    with open(filename, 'w') as f:
        f.write(t)    
    print('written to:', filename)

if __name__ == '__main__':
    main()
