
import urllib.request
import urllib.parse
import os
import json
import datetime
import sys
import csv
import xml.etree.ElementTree
import math

import colorsys


# http://om.yr.no/verdata/vilkar/
# «Weather forecast from Yr, delivered by the Norwegian Meteorological Institute and NRK» (engelsk).
# Link to https://www.yr.no/place/Ocean/57.484_-1.363/
def yr_hourly_forecast(lat, lon):
    url = "https://www.yr.no/place/Ocean/{}_{}/forecast_hour_by_hour.xml".format(lat, lon)
    d = urllib.request.urlopen(url).read()
    root = xml.etree.ElementTree.fromstring(d)

    def extract(e):
        e.find('windDirection')
        flat = {
            'windspeed': float(e.find('windSpeed').get('mps')),
            'winddirection': float(e.find('windDirection').get('deg')),
            'timestamp': 0,
            'longitude': lon,
            'latitude': lat,
        }
        return flat
    
    path = 'forecast/tabular/time'
    return [ extract(e) for e in root.findall(path) ]



def map_linear(val, inmin=0, inmax=1.0, outmin=0, outmax=1.0):
    return (val-inmin) * (outmax-outmin) / (inmax-inmin) + outmin

def wind_sequence(windspeeds, duration, oversampling):

    sequence_length = oversampling*len(windspeeds)
    fs = sequence_length / duration 
    print('samplingrate', fs)
    events = []
    for i in range(0, sequence_length):
        speed = windspeeds[i//oversampling]
        modrate = 0.5 # TODO: make random?
        f = 0.2
        mod = (1.0 + math.sin(2*math.pi*f*(i/fs)) ) / 2.0
        #speed *= (modrate * mod)
        out = map_linear(speed, 0.0, 32.7, 0, 32767) # beauforth_max to int16_max
        events.append(out)

    return events

def gen_c(vals, name='wind_data', ctype='int16_t'):
    numbers = [ str(int(v)) for v in vals ]
    r = "static const {} {}[] = {{ {} }};".format(ctype, name, ','.join(numbers))
    return r

def output_data(events):
    vals = [ v for v in events ]
    t = gen_c(vals, name='speeds')
    filename = 'data.h'
    with open(filename, 'w') as f:
        f.write(t)    
    return filename

def dump_raw(location_name, winds):
    start = datetime.datetime.now().isoformat()
    filename = 'data/{}.{}.csv'.format(location_name, start)

    fields = ['isotime', 'timestamp', 'windspeed', 'winddirection', 'latitude', 'longitude']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for wind in winds: 
            writer.writerow(wind)

        csvfile.flush()

    return filename

def display_colors(brightness=1.0):
    stops = 24

    rgb_values = []

    for step in range(1, stops+1):
        hue = 0.5 - map_linear(step, 1, stops, 0, 0.5)
        #print('hue', hue)
        #hue = hue % 360
        sat = 0.8
        val = 1.0
        if step <= 2:
            sat *= 0.25
        if step <= 4:
            sat *= 0.75
        hsv = hue, sat, val
        rgb = colorsys.hsv_to_rgb(*hsv)
        rgb = [ ch*brightness for ch in rgb ]
        rgb_values.append(rgb)

    def asuint32(rgb):
        r,g,b = rgb
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        #print('rgb', r, g, b)
        return (r<<16) + (g<<8) + (b<<0)

    rgb_ints = [ asuint32(rgb) for rgb in rgb_values ]
    assert len(rgb_ints) == stops
    return rgb_ints

def write_colors():
    on = gen_c(display_colors(brightness=1.0), name='on_colors', ctype='uint32_t')
    off = gen_c(display_colors(brightness=0.12), name='off_colors', ctype='uint32_t')

    with open('colors.h', 'w') as f:
        f.write(on + '\n\n' + off)
    print('wrote colors.h')

def write_beufort():
    points = [0.3, 1.5, 3.3, 5.5, 8.0, 10.8, 13.9, 17.2, 20.7, 24.5, 28.4, 32.6]
    outmax = 32767
    inmax = 32.7
    cpoints = [int( (p/inmax) * outmax ) for p in points]

    bb = gen_c(cpoints, name='beufort_thresholds', ctype='uint16_t')

    assert len(cpoints) == 12
    with open('beufort.h', 'w') as f:
        f.write(bb)
    print('wrote beufort.h')
    

def main():
    location_name = 'hywind-park'
    if len(sys.argv) > 1:
        location_name = sys.argv[1]

    locations = {
        'hywind-park': { 'lat': 57.484, 'lon': -1.363 },
        'old-st-peters-church': { 'lat': 57.504102, 'lon': -1.789955 },
        'buchannes-lighthouse': { 'lat': 57.470447, 'lon': -1.774126 },
        'st-fergus-beach': { 'lat': 57.5599672, 'lon': -1.8152256 },
        'peterhead': { 'q': 'Peterhead,GB' },
    }

    location_info = locations[location_name]
    data = yr_hourly_forecast(**location_info)
    data = data[:24] # FIXME: select proper range
    print('data', len(data), [d['windspeed'] for d in data ])

    assert len(data) == 24, len(data)

    winds = [ w['windspeed'] for w in data ]

    #dump_raw(location_name, winds)

    duration = 24.0
    oversampling = 12
    seq = wind_sequence(winds, duration, oversampling)
    start = [0.0] * 1 * oversampling
    end = [0.0] * 5 * oversampling
    s = start + seq + end

    filename = output_data(s)
    print('written to:', filename)

    write_colors()
    write_beufort()


if __name__ == '__main__':
    main()
