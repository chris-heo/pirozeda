#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# GPIO 23 & 24 set up as inputs. One pulled up, the other down.
# 23 will go to GND when button pressed and 24 will go to 3V3 (3.3V)
# this enables us to demonstrate both rising and falling edge detection
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count = 0

# now we'll define the threaded callback function
# this will run in another thread when our event is detected
def my_callback(channel):
    global count
    count += 1
    

# The GPIO.add_event_detect() line below set things up so that
# when a rising edge is detected on port 24, regardless of whatever 
# else is happening in the program, the function "my_callback" will be run
# It will happen even while the program is waiting for
# a falling edge on the other button.
GPIO.add_event_detect(23, GPIO.RISING, callback=my_callback)

try:
    while True:
        time.sleep(1)
        print "%i Hz" % count
        count = 0
        

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit

GPIO.cleanup()           # clean up GPIO on normal exit
