
import re
import sys

# url https://ukenergy.statoil.com/wind > data/wind.`date --utc +%s`.html

def extract_windspeed(data):
    regex = r'data-windspeed=\"(.*)\"'
    found = re.findall(regex, data)
    if len(found) < 1:
        raise ValueError('Unexpected number of values found: {}', found)
    windspeed = float(found[0])

    return windspeed

def main():
    if len(sys.argv) < 2:
        raise ValueError('Missing argument FILE')
    filepath = sys.argv[1]
    contents = open(filepath, 'r').read()

    w = extract_windspeed(contents)
    print(w)

if __name__ == '__main__':
    main()
