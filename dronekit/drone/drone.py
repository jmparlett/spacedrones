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
from dmath import *
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

############### Constants ####################
#Set up velocity vector to map to each direction.
# vx > 0 => fly North
# vx < 0 => fly South
NORTH = 1
SOUTH = -1

# Note for vy:
# vy > 0 => fly East
# vy < 0 => fly West
EAST = 1
WEST = -1

# Note for vz:
# vz < 0 => ascend
# vz > 0 => descend
UP = -0.5
DOWN = 0.5

################################ Utility Functions ###################################


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
    def __init__(self, connection_string, backtrack = True):
       try:
           self.vehicle = connect(connection_string, wait_ready=True)
       except Exception:
           logging.error("Could not connect to mavlink stream")
       self.logfile_name = logfile_name
       self.backtrack = backtrack
       self.move_record = [] # store record of movements
    
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
    def send_ned_velocity(self, velocity_x, velocity_y, velocity_z, duration):
        """
        Taken from the dronekit examples, on github https://dronekit-python.readthedocs.io/en/latest/examples/
        Move vehicle in direction based on specified velocity vectors and
        for the specified duration.

        This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only 
        velocity components 
        (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned).
        
        Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
        with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
        velocity persists until it is canceled. The code below should work on either version 
        (sending the message multiple times does not cause problems).
        
        See the above link for information on the type_mask (0=enable, 1=ignore). 
        At time of writing, acceleration and yaw bits are ignored.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

        # send command to vehicle on 1 Hz cycle
        for x in range(0,duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)
    
    def condition_yaw(self, heading, relative=True):
        """
        Send MAV_CMD_CONDITION_YAW message to point vehicle at a specified heading (in degrees).

        This method sets an absolute heading by default, but you can set the `relative` parameter
        to `True` to set yaw relative to the current yaw heading.

        By default the yaw of the vehicle will follow the direction of travel. After setting 
        the yaw using this function there is no way to return to the default yaw "follow direction 
        of travel" behaviour (https://github.com/diydrones/ardupilot/issues/2427)

        For more information see: 
        http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
        """
        if relative:
            is_relative = 1 #yaw relative to direction of travel
        else:
            is_relative = 0 #yaw is an absolute angle
        # create the CONDITION_YAW command using command_long_encode()
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
            0, #confirmation
            heading,    # param 1, yaw in degrees
            0,          # param 2, yaw speed deg/s
            1,          # param 3, direction -1 ccw, 1 cw
            is_relative, # param 4, relative offset 1, absolute angle 0
            0, 0, 0)    # param 5 ~ 7 not used
        # send command to vehicle
        self.vehicle.send_mavlink(msg)

       
    def set_velocity_rect(self, v_x, v_y, v_z, duration, SPEED=1):
        '''
        Given these parameters we will set velocity vectors of drone accordingly
        '''
        
        if self.backtrack: # if set save movements so we can backtrack later
            self.move_record.append((v_x, v_y, v_z, duration))
        self.send_ned_velocity(SPEED*v_x, SPEED*v_y, SPEED*v_z, duration)

    #  def move_sphereical(self, p, theta, phi):
        #  v_x, v_y, v_z = sTor(p, theta, phi)
        #  self.move_rect(v_x, v_y, v_z, int(p))

    def backtrack_movements(self):
        # turn off movement recording so we dont loop forever
        self.backtrack = False

        while self.move_record != []:
            v_x, v_y, v_z, duration = self.move_record.pop()
            v_x, v_y, v_z  = invert(v_x, v_y, v_z)
            #  print("moves left", len(self.move_record))
            #  print(v_x, v_y, v_z)
            self.set_velocity_rect(v_x, v_y, v_z, duration)

        # re-enable backtracking in case our flight isn't finished
        self.backtrack = False

    def move_to_point_R(self, x,y,z):
        dur = magnitude(x,y,z)
        self.set_velocity_rect(x/dur, y/dur, z/dur, int(dur))


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
    #  drone.move(0,0,1,5)

    #  moves_r = [(1,0,0,5),
             #  (0,1,0,5),
             #  (-1,0,0,5),
             #  (0,-1,0,5)]
#
    #  moves_s = [(5,90,90),
             #  (5,0,90),
             #  (5,90,90),
             #  (5,80,90)]
    #  fly hex
    #  for m in moves_r:
        #  x,y,z, dur = m
        #  drone.set_velocity_rect(x,y,z, dur)

    #  fly back
    #  for m in moves_r[::-1]:
        #  x,y,z, dur = m
        #  x,y,z = invert(x,y,z)
        #  drone.set_velocity_rect(x, y, z, dur)

    # fly by points
    drone.move_to_point_R(5,0,0)
    drone.move_to_point_R(0,5,0)
    drone.move_to_point_R(-5,0,0)
    drone.move_to_point_R(0,-5,0)
    
    # land the drone and close the connection
    #  drone.land_and_close()
