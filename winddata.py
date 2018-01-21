
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
    

def download_current(api_token, **kwargs):
    base = "https://api.openweathermap.org/data/2.5/weather"
    args = kwargs
    args['appId'] = api_token
    url = base + '?' + urllib.parse.urlencode(kwargs)
    print('GET:', url)
    d = urllib.request.urlopen(url).read()
    data = json.loads(d)
    return data

def download_forecast(api_token, **kwargs):
    base = "https://api.openweathermap.org/data/2.5/forecast"
    args = kwargs
    args['appId'] = api_token
    url = base + '?' + urllib.parse.urlencode(kwargs)
    print('GET:', url)
    d = urllib.request.urlopen(url).read()
    data = json.loads(d)
    return data


def extract_current_wind(weather):
    assert len(weather['weather']) == 1, 'multiple weather reports'
    flat = {
        'windspeed': weather['wind'].get('speed'),
        'winddirection': weather['wind'].get('deg'),
        'timestamp': weather['dt'],
        'longitude': weather['coord']['lon'],
        'latitude': weather['coord']['lat']
    }
    flat['isotime'] = datetime.datetime.fromtimestamp(flat['timestamp']).isoformat()
    return flat

def extract_wind_forecast(forecast):
    def extract(weather):
        flat = {
            'windspeed': weather['wind'].get('speed'),
            'winddirection': weather['wind'].get('deg'),
            'timestamp': weather['dt'],
            'longitude': forecast['city']['coord']['lon'],
            'latitude': forecast['city']['coord']['lat']
        }
        return flat
    return [ extract(w) for w in forecast['list'] ]

def main():
    token = os.environ.get('OPENWEATHERMAP_TOKEN', None)
    if not token:
        raise ValueError("Missing API token")

    location_name = 'hywind-park'
    if len(sys.argv) > 1:
        location_name = sys.argv[1]

    timeinterval = 10*60
    if len(sys.argv) > 2:
        timeinterval = int(sys.argv[2])    

    start = datetime.datetime.now().isoformat()
    filename = 'data/{}.{}.csv'.format(location_name, start)

    # From email
    locations = {
        'hywind-park': { 'lat': 57.484, 'lon': -1.363 },
        'old-st-peters-church': { 'lat': 57.504102, 'lon': -1.789955 },
        'buchannes-lighthouse': { 'lat': 57.470447, 'lon': -1.774126 },
        'st-fergus-beach': { 'lat': 57.5599672, 'lon': -1.8152256 },
        'peterhead': { 'q': 'Peterhead,GB' },
    }

    location_info = locations[location_name]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['isotime', 'timestamp', 'windspeed', 'winddirection', 'latitude', 'longitude'])

        print('writing to:', filename)

        params = location_info

        winds = yr_hourly_forecast(**params)
        print('info:', json.dumps(winds))

        for wind in winds: 
            writer.writerow(wind)

        csvfile.flush() # ensure data hits disk regularly


if __name__ == '__main__':
    main()
