
import urllib.request
import urllib.parse
import os
import json
import datetime
import sys
import csv
import xml.etree.ElementTree

import gevent


# http://om.yr.no/verdata/vilkar/
# «Weather forecast from Yr, delivered by the Norwegian Meteorological Institute and NRK» (engelsk).
# Link to https://www.yr.no/place/Ocean/57.484_-1.363/
def yr_hourly_forecast(lat, lon):
    url = "https://www.yr.no/place/Ocean/{}_{}/forecast_hour_by_hour.xml".format(lat, lon)
    d = urllib.request.urlopen(url).read()
    root = xml.etree.ElementTree.fromstring(d)
    print('r', root)

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

def wind_sequence(windspeeds):
    windspeeds = windspeeds[:24] # FIXME: select proper range
    assert len(windspeeds) == 24, len(windspeeds) 

    events = []
    for speed in windspeeds:
        v = map_linear(speed, 0.0, 32.7, 0, 32767) # beauforth_max to int16_max
        events.append(v)

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
    winds = [ w['windspeed'] for w in data ]
    #dump_raw(location_name, winds)

    s = wind_sequence(winds)

    filename = output_data(s)
    print('written to:', filename)



if __name__ == '__main__':
    main()
