import rospy
from geometry_msgs.msg import PoseStamped
from pymavlink import mavutil
from nav_msgs.msg import Path
import time
import utm


class GoalToMAVLink:
    def __init__(self):

        # Initialize node
        rospy.init_node('goal_to_mavlink', anonymous=True)
        
        # Set up MAVLink connection
        self.mav_connection = mavutil.mavlink_connection('udpin:localhost:14550')
        rospy.loginfo("Connected to MAVLink")
        self.check_heartbeat(self.mav_connection)
        self.waypoints = []
        self.mavlink_waypoints = []

        self.processing_waypoints = False
        self.latest_seq = -1

        # Subscribe to the goal topic
        rospy.Subscriber('/move_base/NavfnROS/plan', Path, self.goal_callback)
        rospy.spin()
    
    def goal_callback(self, msg):

        self.waypoints = [(pose.pose.position.x, pose.pose.position.y) for pose in msg.poses]
        print("Received path with {} waypoints".format(len(self.waypoints)))

        self.clear_all_missions(self.mav_connection)

        self.mavlink_waypoints = self.convert_to_mavlink_waypoints(self.waypoints)

        self.upload_mission(self.mav_connection, self.mavlink_waypoints)

        self.set_mode(self.mav_connection, "GUIDED")

        self.arm_drone(self.mav_connection)

        self.set_mode(self.mav_connection, "AUTO")

        self.start_mission(self.mav_connection)

        print("All steps done!")
        
    def check_heartbeat(self, connection):
        while True:
            msg = connection.recv_match(type="HEARTBEAT", blocking=True)
            if msg:
                print(f"Heartbeat received {msg}")
                return True


    def get_current_position(self, mav_connection):
        mav_connection.wait_heartbeat()

        while True:
            # msg = mav_connection.recv_match(type="HEARTBEAT", blocking=True) 
            gps_msg = mav_connection.recv_match(type="GLOBAL_POSITION_INT", blocking=True)

            current_lat = gps_msg.lat / 1e7
            current_lon = gps_msg.lon / 1e7
            current_alt = gps_msg.alt / 1e3

            return current_lat, current_lon, current_alt

    def convert_to_mavlink_waypoints(self, waypoints):
        mavlink_waypoints = []
        seq = 0
        current_lat, current_lon, current_alt = self.get_current_position(self.mav_connection)

        # current_utm = utm.from_latlon(current_lat, current_lon)
        # current_easting, current_northing, zone_number, zone_letter = current_utm

        # print(f"Current coords of drone: {current_lat}, {current_lon}")

        for wp in waypoints:
            x, y = wp
            # print(f"Preparing to send lat: {x}, lon: {y}, seq: {seq}")

            # global_easting = current_easting + x
            # global_northing = current_northing + y

            # global_lat, global_lon = utm.to_latlon(global_easting, global_northing, zone_number, zone_letter)

            waypoint = mavutil.mavlink.MAVLink_mission_item_int_message(
                target_system=1,  # Target system ID
                target_component=0,  # Target component ID
                seq=seq,  # Sequence number
                frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                current=0 if seq > 0 else 1,  # Current waypoint (0 for all except the first)
                autocontinue=1,  # Autocontinue to the next waypoint
                param1=0,  # Hold time in decimal seconds
                param2=0,  # Acceptance radius in meters (0 to use default)
                param3=0,  # Pass through waypoint (0 to use default)
                param4=float('nan'),  # Desired yaw angle (NaN to use default)
                x=int(x * 1e7),  # Latitude in degrees * 1e7
                y=int(y * 1e7),  # Longitude in degrees * 1e7
                z=current_alt  # Altitude in meters (adjust as needed)
            )

            mavlink_waypoints.append(waypoint)
            # print(f"Waypoint from function: {waypoint}")
            seq += 1

        return mavlink_waypoints
    
    def upload_mission(self, connection, waypoints):
        connection.mav.mission_count_send(
            target_system=1,
            target_component=0,
            count=len(waypoints)
        )
        print("Sent MISSION_COUNT command")
        self.await_ack(connection, 'MISSION_ACK')

        for wp in waypoints:
            connection.mav.send(wp)
            print("Sent waypoint: {}".format(wp))
            rospy.sleep(0.1)
        
        print("All waypoints sent.")
        self.await_ack(connection, 'MISSION_ACK')

    def start_mission(self, connection):
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_MISSION_START,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        print("Sent MISSION_START command.")
        self.await_ack(connection, 'COMMAND_ACK')


    def clear_all_missions(self, connection):
        connection.mav.mission_clear_all_send(
            target_system=1,
            target_component=0
        )
        print("Sent Mission_clear_all command")
        self.await_ack(connection, "MISSION_ACK")


    def await_ack(self, connection, ack_type):
        while True:
            print("Getting ack from await")
            msg = connection.recv_match(blocking=True)
            if msg:
                if msg.get_type() == ack_type:
                    print(f"Received {ack_type}: {msg}")
                    return
                else:
                    print("No ack_type received but this: ", msg)
                    return


    def set_mode(self, connection, mode):
        mode_id = connection.mode_mapping().get(mode)
        if mode_id is None:
            print(f"Mode {mode} not recognized.")
            return
        
        connection.set_mode(mode_id)
        print(f"Sent mode change to {mode}.")
        self.await_ack(connection, 'COMMAND_ACK')

    
    def arm_drone(self, connection):
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0
        )
        print("Sent arm command.")
        self.await_ack(connection, 'COMMAND_ACK')

    def disarm_drone(self, connection):
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        print("Sent disarm command.")
        self.await_ack(connection, 'COMMAND_ACK')


    def request_mission_list(self, connection):
        connection.wait_heartbeat()

        connection.mav.mission_request_list_send(
            target_system=1,  # Target system ID
            target_component=0  # Target component ID
        )
        print("Sent MISSION_REQUEST_LIST command.")

        # Wait for the MISSION_COUNT message
        msg = connection.recv_match(type='MISSION_COUNT', blocking=True)
        if msg:
            mission_count = msg.count
            print(f"Received MISSION_COUNT: {mission_count} missions.")
            
            # Request each mission item
            for seq in range(mission_count):
                connection.mav.mission_request_int_send(
                    target_system=1,  # Target system ID
                    target_component=0,  # Target component ID
                    seq=seq  # Sequence number
                )
                print(f"Requested mission item {seq}.")

                # Wait for the MISSION_ITEM_INT message
                msg = connection.recv_match(type='MISSION_ITEM_INT', blocking=True)
                if msg:
                    print(f"Received mission item {msg.seq}: lat={msg.x}, lon={msg.y}, alt={msg.z}")


if __name__ == '__main__':
    try:
        GoalToMAVLink()
    except rospy.ROSInterruptException:
        pass
