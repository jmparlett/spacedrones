# imports
import rpi.GPIO as GPIO
import time

# GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# set pin 11 as output pin and define servo1 as PWM pin
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # pin 11 for servo1

# Start PWM running, with value of 0
servo1.start(0)
# wait to settle
time.sleep(2)

# move the rotor
print("rotate 180")

#define var duty

for duty in range(2,12):
    servo1.ChangeDutyCycle(duty)
    time.sleep(1)
    
# wait few secs
time.sleep(2)

# turn back 90
print("Turn back 90")
servo1.ChangeDutyCycle(7)
time.sleep(2)
