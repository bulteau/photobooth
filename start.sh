#!/bin/sh
cd home/pi/Documents/camera/www/

nohup sudo python ./photobooth.py &
nohup sudo python ./photobooth-web.py  > /dev/null 2>&1&
