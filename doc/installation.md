# Software setup

## Prerequisites

The following must be installed already

* Arduino IDE
* Python 3
* git

### Download the code

In a terminal

    cd Downloads
    git clone http://github.com/jonnor/windportal

# Making updates

Get latest code

    cd Downloads/windportal
    git pull origin master

Fetch latest weather data

    python3 windportal.py

Flash the firmware to Arduino

    Open `windportal.ino` Arduino IDE, hit "Upload"
