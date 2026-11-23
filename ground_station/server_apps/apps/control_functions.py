import sys
import argparse
from pymavlink import mavutil
from math import floor
import time


def set_mode(mav_connection, mode):
    mav_connection.wait_heartbeat()

    if mode not in mav_connection.mode_mapping():
        print("Unkown mode: {}".format(mode))
        print('Try: ', list(mav_connection.mode_mapping.keys()))
        sys.exit(1)

    mode_id = mav_connection.mode_mapping()[mode]

    mav_connection.mav.set_mode_send(
        mav_connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

    msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print("MODE_SET RESULT: ", msg)
    
    if msg.result != 0:
        return False
    return True


def get_takeoff_position(mav_connection):
    mav_connection.wait_heartbeat()

    msg = mav_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg is None:
        print("home_position msg is None")
    else:
        home_position = {'lat': msg.lat / 1e7, 'lng': msg.lon / 1e7,
                    'alt': msg.alt / 1e3}
    
        return home_position

# -------- MOVEMENT FUNCTION --------


def NED_position(mav_connection, rounded, positiveZ=False):
    mav_connection.wait_heartbeat()

    msg = mav_connection.recv_match(type="LOCAL_POSITION_NED", blocking=True)
    x = msg.x
    y = msg.y
    z = msg.z

    if rounded:
        x, y, z = floor(x), floor(y), floor(z)
    
    if positiveZ:
        z *= -1

    return x, y, z


def arm(mav_connection, arm_command):
    # Wait for the first heartbeat
    # This sets the system and component ID of remote system for the link

    # arm command = 1 for arming drone, 0 for disarming
    mav_connection.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" %
          (mav_connection.target_system, mav_connection.target_component))

    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, arm_command, 0, 0, 0, 0, 0, 0)
    
    msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print("ARM RESULT: ", msg)

    if msg.result != 0:
        print("Error: ARM command failed...")
        return False
    return True


def takeoff(mav_connection, amount):

    mav_connection.wait_heartbeat()

    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                         mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
                                         0, 0, 0, 0, 0, 0, amount)
    
    msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    
    if msg.result != 0:
        print("Error TAKEOFF command failed")
        return False
    return True


def land_drone(mav_connection, return_home):
    mav_connection.wait_heartbeat()

    print("Landing at the spot...")
    set_mode(mav_connection, 'LAND')


def movement(mav_connection, movement):
    mav_connection.wait_heartbeat()
    
    x, y, z = movement
    
    mav_connection.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            10, mav_connection.target_system, mav_connection.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, int(0b100111111000), x, y, -z, 0, 0, 0, 0, 0, 0, 0, 0,
        ) # z is negative because the command expects - values
    )


def global_movement(mav_connection, lat, lon, alt):
    mav_connection.mav.set_position_target_global_int_send(
                0,  # time_boot_ms
                1,  # target_system
                1,  # target_component
                mavutil.mavlink.MAV_FRAME_GLOBAL_INT,  # frame
                0b0000111111111000,  # type_mask (ignore all but lat and lon)
                int(lat * 1e7),  # lat (scaled to 1e7)
                int(lon * 1e7),  # lon (scaled to 1e7)
                alt,  # alt (altitude in mm, not used)
                0,  # vx (not used)
                0,  # vy (not used)
                0,  # vz (not used)
                0,  # afx (not used)
                0,  # afy (not used)
                0,  # afz (not used)
                0,  # yaw (not used)
                0  # yaw_rate (not used)
            )
    
def send_global_velocity(mav_connection, latitude, longitude, altitude, velocity_x, velocity_y, velocity_z, duration):
    for _ in range(duration):
        mav_connection.mav.set_position_target_global_int_send(
            0,  # time_boot_ms (not used)
            mav_connection.target_system,
            mav_connection.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # frame
            0b0000111111000111,  # type_mask (only velocities enabled)
            int(latitude * 1e7),  # lat_int (degrees * 1E7)
            int(longitude * 1e7),  # lon_int (degrees * 1E7)
            altitude,  # alt (meters)
            velocity_x,  # vx (m/s)
            velocity_y,  # vy (m/s)
            velocity_z,  # vz (m/s)
            0, 0, 0,  # afx, afy, afz (acceleration)
            0, 0  # yaw, yaw_rate
        )
        time.sleep(1)  # Adjust the sleep time as needed

        


def yaw(mav_connection, arguments):
    mav_connection.wait_heartbeat()

    yaw, speed, cw, rel = arguments
    
    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                         mavutil.mavlink.MAV_CMD_CONDITION_YAW,0,
                                         yaw, speed, cw, rel, 0, 0, 0)

    msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    print("YAW RESULT: ",msg)


def changeSpeed(mav_connection, speed):
    mav_connection.wait_heartbeat()


    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,0,
                                        0, speed, 0, 0, 0, 0, 0)
    
    msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print("SPEED RESULT: ",msg)
