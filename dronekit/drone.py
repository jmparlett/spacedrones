'''
This module will provide the main interface to control our drone.
It will utilize dronekit and mavlink to interface with the drone.
The drone will write to a logfile in the format {date_string}:dronelogs.log.
'''

# Logging levels
# debug
# info
# warning
# critical

############## Dependecies ################
### Standard packages ###
import time
import math
import socket
import argparse
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, APIException
import logging

############### Logging Settings ####################
date_string = time.asctime().replace(" ","_").lower()
logfile_name = f"{date_string}:dronelogs.log"
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s')
        #  filename=logfile_name)

#################### GOTO for movement by n/e from current locations in meters #######################
# These function are used in the calculation of movement for the goto functions
def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
    else:
        raise Exception("Invalid Location object passed")

    return targetlocation;


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


class Drone:
    def __init__(self, connection_string):
       try:
           self.vehicle = connect(connection_string,wait_ready=True)
       except Exception:
           logging.error("Could not connect to mavlink stream")
       self.logfile_name = logfile_name
    
    def get_logfile(self):
        '''
        returns logfile name
        '''
        return self.logfile_name

    def arm_and_takeoff(self,target_altitude):
        '''
        Arms vehicle and flies to target altitude in meters
        '''

        logging.info("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            logging.info(" Waiting for vehicle to initialise...")
            time.sleep(1)

        logging.info("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            logging.info(" Waiting for arming...")
            time.sleep(1)

        logging.info("Taking off!")
        self.vehicle.simple_takeoff(target_altitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            logging.info("Altitude: %lf", self.vehicle.location.global_relative_frame.alt)
            #Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt>=target_altitude*0.95:
                logging.info("Reached target altitude")
                break
            time.sleep(1)

    ###################### Movement ###########################
    def goto(self, dNorth, dEast):
        '''
        This function moves the drone to a position relative to its currentLocation according to the following scheme.
        dNorth = forward
        dEast = right 
        -dNorth = forward
        -dEast = left
        '''
        gotoFunction=self.vehicle.simple_goto
        currentLocation=self.vehicle.location.global_relative_frame
        targetLocation=get_location_metres(currentLocation, dNorth, dEast)
        targetDistance=get_distance_metres(currentLocation, targetLocation)
        gotoFunction(targetLocation)

        prevRemainingDistance=0
        repCount=0 #number of times we've encountered to same distance
        while self.vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
            
            if repCount > 4:
                break # we're stuck in a loop better to leave
            remainingDistance=get_distance_metres(self.vehicle.location.global_frame, targetLocation)
            if remainingDistance>=(prevRemainingDistance-0.01):
                repCount+=1
            #  if remainingDistance<=targetDistance*0.1: #Just below target, in case of undershoot.
            if remainingDistance<=targetDistance*0.25: #Just below target, in case of undershoot.
                logging.info("Reached target")
                break;
            # log remaining distance so we can visualize
            #  print(type(remainingDistance), "is type of remainingDistance")
            logging.info("Distance to target: %f",remainingDistance)
            time.sleep(2)
            prevRemainingDistance=remainingDistance

    def move_left(self):
        '''
        move vehicle 1 meter left of current position
        '''
        self.goto(0,-1)

    def move_right(self):
        '''
        move vehicle 1 meter right of current position
        '''
        self.goto(0,1)

    def move_forward(self):
        '''
        move vehicle 1 meter forward of current position
        '''
        self.goto(1,0)
    
    def move_back(self):
        '''
        move vehicle 1 meter backward of current position
        '''
        self.goto(-1,0)

    def land_and_close(self):
        logging.info('Returning to Launch')
        self.vehicle.mode = VehicleMode("RTL")
        #  Close vehicle object before exiting script
        logging.info('Close vehicle object')
        self.vehicle.close()



if __name__ == "__main__":
    # connect to virtual stream
    drone = Drone("127.0.0.1:14550")
    
    # take off to target altitude
    drone.arm_and_takeoff(5)

    # fly a box
    drone.move_forward()
    drone.move_left()
    drone.move_back()
    drone.move_right()
    
    # land the drone and close the connection
    drone.land_and_close()
