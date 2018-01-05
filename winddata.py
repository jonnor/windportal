
import urllib.request
import urllib.parse
import os
import json
import datetime
import sys
import csv

import gevent

def download_current(api_token, **kwargs):
    base = "https://api.openweathermap.org/data/2.5/weather"
    args = kwargs
    args['appId'] = api_token
    url = base + '?' + urllib.parse.urlencode(kwargs)
    print('GET:', url)
    d = urllib.request.urlopen(url).read()
    data = json.loads(d)
    return data

def extract_wind(weather):
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
        'peterhead': { 'q': 'Peterhead' },
    }

    location_info = locations[location_name]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['isotime', 'timestamp', 'windspeed', 'winddirection', 'latitude', 'longitude'])

        print('writing to:', filename)
        while True:
            params = location_info

            weather = download_current(token, **params)
            print('rawinfo:', weather)        
            wind = extract_wind(weather)
            print('extracted:', wind)
            writer.writerow(wind)
            csvfile.flush() # ensure data hits disk regularly

            gevent.sleep(timeinterval)

if __name__ == '__main__':
    main()
