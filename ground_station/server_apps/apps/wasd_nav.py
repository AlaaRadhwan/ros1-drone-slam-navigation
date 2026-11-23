import time
from pymavlink import mavutil

forward_velocity = 0
left_velocity = 0

# Adjust as needed
acceleration_rate = 0.1
deceleration_rate = 0.2


def wasd_movement(mav, updated_pos, key):

    alt = -1 * updated_pos[2]

    def move_forward():
        global forward_velocity
        forward_velocity += acceleration_rate
        # forward_velocity = min(1, forward_velocity) # Limit max velocity to 1
        send_velocity_command(forward_velocity, left_velocity)


    def move_backward():
        global forward_velocity
        forward_velocity -= acceleration_rate
        # forward_velocity = max(-1, forward_velocity)
        send_velocity_command(forward_velocity, left_velocity)


    def move_left():
        global left_velocity
        left_velocity -= acceleration_rate
        # left_velocity = max(-1, left_velocity)
        send_velocity_command(forward_velocity, left_velocity)


    def move_right():
        global left_velocity
        left_velocity += acceleration_rate
        # left_velocity = min(1, left_velocity)
        send_velocity_command(forward_velocity, left_velocity)


    def send_velocity_command(forward_velocity, left_velocity):

        mav.mav.set_position_target_local_ned_send(
            0,
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111000000,
            forward_velocity, # x (forward)
            left_velocity, # y (left)
            -8,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )

    print(f"updated_pos: {updated_pos}")

    if key == 'w':
        move_forward()

    elif key == 'a':
        move_left()
    elif key == 's':
        move_backward()
    elif key == 'd':
        move_right()
