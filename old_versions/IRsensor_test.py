import RPi.GPIO as gp
from time import sleep
gp.setmode(gp.BOARD)
gp.setup(16,gp.IN)
# OUT(signal): GPIO 23, physical pin 16
# GND: physical pin 9 (recommend)
# VCC: physical pin 1 (recommedn)
while True:
    try:
        if (not gp.input(16)) == True:
            print("Obstacle")
        elif (not gp.input(16)) == False:
            print("Clear")
    except KeyboardInterrupt:
        gp.cleanup()
        break
