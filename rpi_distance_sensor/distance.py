import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM) #so refer to pins by BCM numbers?
speed_constant = 17150 #speed of sound at sea level = 343ms. Remember speed of sound differs based on the medium.
                       # converts to 34300cm then we divide by 2 for our distance one way calc making it 17150cm

trig = 23 #pin 16
echo = 24 #pin 18

def distance():
    print("were measureing distance")

    gpio.setup(trig,gpio.OUT) #trig is out since it is the receving signal on the sensor. It tells it to send
    gpio.setup(echo,gpio.IN)  #echo is the signal sent when a sound wave gets back to the sensor

    gpio.output(trig,False) #output should be 0 or "set low"

    print("sensor settling")

    time.sleep(2)# stop ececuting for 2 seconds

    # The sensor must receive a 10 microsecond long pulse to start the ranging program. 
    # To accomplish this we set trig pin high for 10uS.

    gpio.output(trig,True)
    time.sleep(0.00001)
    gpio.output(trig,False)


    # The sensor will set the echo pin high for the same amount of time it takes for a wave to go and come back.
    # By measureing time it takes for pin to become low we can calculate distance from formula (Distance = Speed * Time)

    # start timestamp 
    while gpio.input(echo) == 0:
        pulse_start = time.time()

    # stop timestamp 
    while gpio.input(echo)==1:
        pulse_end = time.time()

    pulse_duration = (pulse_end - pulse_start) # remeber we only care about time to target for distance calc, but
                                                 # sensor tells us time it takes to reach and return from target so we divide by 2.
    distance  = speed_constant*pulse_duration
    distance = round(distance,2) # for neatness
    print(f"Distance to object in CM: {distance}")
