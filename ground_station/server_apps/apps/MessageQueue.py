import threading
import time
from pymavlink import mavutil
from apps.control_functions import *
from apps.return_to_launch import *


class MessageQueue:
    def __init__(self, lock, mav_connection):
        self.queue = []
        self.lock = lock
        self.mav_connection = mav_connection

    
    def add_command(self, command, *args):
        print("Adding commands...")
        with self.lock:
            self.queue.append((command, args))
            print("Added.")
    
    def exeute_commands(self):
        print("Executing commands...")
        with self.lock:
            while self.queue:
                command, args = self.queue.pop(0)
                send_function, send_args = COMMAND_FUNCITONS.get(command, (None, None))
                if send_function:
                    send_function(self.mav_connection, *args)
                else:
                    print("Uknown command: ", command)

            print("Executed the commands")



COMMAND_FUNCITONS = {
    "SET_MODE": (set_mode, ()),
    "ARM": (arm, (1,)),
    "DISARM": (arm, (0,)),
    "TAKEOFF": (takeoff, (4)),
    "LAND": (land_drone, (False)),
    "RTL": (advanced_rtl, ()),
    "YAW": (yaw, ([0, 0, 0, 0])),
}
