from distance import getDistance
from accesscamera import snapshot
from time import sleep


while(1):
    distance = getDistance()
    if distance < 10:
        print("Distance to target is", distance, "capturing image") 
        snapshot()
    else:
        print("Distance to target is", distance) 
    sleep(1) 
