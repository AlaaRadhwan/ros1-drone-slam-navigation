import time
from pymavlink import mavutil

# --------------------------------------
# CHECK IF VEHICLE IS SAFE
# --------------------------------------

def is_vehicle_safe(mav):
    heartbeat_status = False
    gps_status = False
    altitude_status = False 
    battery_voltage_status = False

    # Check heartbeat and mode
    # while True:
    #     print("Checking vehicle...")
    #     msg = mav.recv_msg()
    #     if msg:
    #         print("got heartbeat")
    #         mode = mavutil.mode_mapping_acm[msg.custom_mode]
    #         if mode == 'GUIDED' and msg.system_status == mavutil.mavlink.MAV_STATE_STANDBY:
    #             print("Vehicle is in a safe state for return to launch.")
    #             break

    #         else:
    #             print("There was a problem with heartbeat check")
    #             break
    #     time.sleep(1)
    
    # Check GPS fix
    while True:
        print("Checking GPS fix...")
        # mav.wait_heartbeat()

        msg = mav.recv_match('GLOBAL_POSITION_INT')

        if msg:
            print("Recived message...")
            if msg.lat != 0 and msg.lon != 0:
                print("GPS fis is stable...")
                gps_status = True
                break
            else:
                print("There was a problem with gps check")
                break
        # time.sleep(1)
    
    # Check altitude
    while True:
        msg = mav.recv_msg()
        if msg and msg.get_type() == 'GLOBAL_POSITION_INT':
            altitude = msg.alt / 1000.0  # Convert altitude from mm to meters
            if altitude > 5.0:  # Replace 5.0 with your minimum safe altitude
                print(f"Altitude is safe ({altitude} meters). Vehicle is ready for return to launch.")
                altitude_status = True
                break
            else:
                print("There was a problem with altitude check")
                break
        time.sleep(1)

    # Check battery level
    while True:
        msg = mav.recv_msg()
        if msg and msg.get_type() == 'SYS_STATUS':
            battery_voltage = msg.voltage_battery / 1000.0  # Convert voltage from mV to V
            if battery_voltage > 10.0:  # Replace 12.0 with your minimum safe battery voltage
                print(f"Battery level is safe ({battery_voltage} V). Vehicle is ready for return to launch.")
                battery_voltage_status = True
                break
            else:
                print("There was a problem with battery check")
                break
        time.sleep(1)
    
    if battery_voltage_status and altitude_status \
        and heartbeat_status and gps_status:
        return True
    else:
        return False



# --------------------------------------
# ADVANCED RETURN TO LAUNCH FUNCTION
# --------------------------------------

def advanced_rtl(mav):
    mav.wait_heartbeat()


    print("Sending RTL command...")
    print('-'*20)

    mav.mav.command_long_send(
        mav.target_system,      # Target system ID
        mav.target_component,   # Target component ID
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
        0, 0, 0,
        0, 0, 0, 0, 0
    )

    msg = mav.recv_match(type='COMMAND_ACK', blocking=True)

    if msg.result != 0:
        return False
    
    return True
