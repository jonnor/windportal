interval=300

while true
do
    timestamp=`date --utc +%s`
    filename="data/wind.$timestamp.html"
    curl https://ukenergy.statoil.com/wind > $filename
    echo "wrote $filename"
    windspeed=`python3 scrapewind.py $filename`
    echo "wind was: $windspeed"
    echo ",$timestamp,$windspeed,,," >> data/wind.scraped.csv
    sleep $interval
done
