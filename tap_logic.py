# ----------------------- PINOUT ---------------------------
# flow sensor
# Pin 1(red) - 5V (physical pin 4)
# Pin 2(yellow) - gpio (here P1-8, gpio 14, TXD is used) (physical pin 8)
# Pin 3(black) - Ground (physical pin 6)
# No water: high
# Waterflow: low
# 
# IR sensor
# OUT(signal): physical pin 3
# GND: physical pin 9 
# VCC: physical pin 1 

# ----------------------- Flow sensor ----------------------------
import time
import pigpio
# ----------------------- IR sensor ------------------------------
import RPi.GPIO as gp
from time import sleep

# ------------------------ core variables ---------------------------
flow_ttime = 0.0
tap_on = False
# ------------------------ Flow sensor sample code ---------------------------
HALL=14

pi = pigpio.pi() # connect to local Pi

pi.set_mode(HALL, pigpio.INPUT)
pi.set_pull_up_down(HALL, pigpio.PUD_UP)

start = time.time()

# while (time.time() - start) < 60:
#   print("Hall = {}".format(pi.read(HALL)))
#   time.sleep(0.2)

# pi.stop() # end placed at end of program

# -----------------------IR sensor sample code----------------------------
IR_OUT = 3

gp.setmode(gp.BOARD)
gp.setup(IR_OUT,gp.IN)

# while True: 
    # try:
        # if (not gp.input(IR_OUT)) == True:
            # print("Obstacle")
        # elif (not gp.input(IR_OUT)) == False:
            # print("Clear")
    # except KeyboardInterrupt:
        # gp.cleanup()
        # break
        
# ---------------------Valve----------------------
valve = 10 # physical pin 10

pi.set_mode(valve, pigpio.OUTPUT)
pi.set_pull_up_down(valve, pigpio.PUD_DOWN)

testclk = 0
while True:
   # if testclk == 0: # testing code
      # tap_on = True
      # testclk = 1
      # time.sleep(3.0)
   # elif testclk == 1:
      # tap_on = False
      # testclk = 0
      # time.sleep(3.0)
   try: # IR response
      if (not gp.input(IR_OUT)) == True: # if detected
         tap_on = True
         print("presence detected")
      elif (not gp.input(IR_OUT)) == False: # if not detected
         tap_on = False
         print("presence not detected")
   except KeyboardInterrupt:
      gp.cleanup()
      break
   try: # valve
      if tap_on == True:
         pi.write(valve, 1)
         print("tap is on")
      else:
         pi.write(valve, 0)
         print("tap is off")
   except KeyboardInterrupt:
         gp.cleanup()
         break
   time.sleep(1.0)

# ---------------------PRINT----------------------
# WIP

# ---------------------end------------------------
pi.write(valve,0)
pi.stop()


