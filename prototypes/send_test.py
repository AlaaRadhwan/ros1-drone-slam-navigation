import rospy
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


def convert_to_mavlink_waypoints(waypoints):
    mavlink_waypoints = []
    seq = 0
    for wp in waypoints:
        x, y = wp
        # Set appropriate values for the MAVLink message fields
        waypoint = mavutil.mavlink.MAVLink_mission_item_int_message(
            target_system=1,  # Target system ID
            target_component=0,  # Target component ID
            seq=seq,  # Sequence number
            frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            current=0,  # Current waypoint (0 for all except the first)
            autocontinue=1,  # Autocontinue to the next waypoint
            param1=0,  # Hold time in decimal seconds
            param2=0,  # Acceptance radius in meters (0 to use default)
            param3=0,  # Pass through waypoint (0 to use default)
            param4=float('nan'),  # Desired yaw angle (NaN to use default)
            x=int(x * 1e7),  # Latitude in degrees * 1e7
            y=int(y * 1e7),  # Longitude in degrees * 1e7
            z=10  # Altitude in meters (adjust as needed)
        )
        mavlink_waypoints.append(waypoint)
        seq += 1
    return mavlink_waypoints

class PathSubscriber:
    def __init__(self):
        rospy.init_node("path_subscriber", anonymous=True)
        self.path_sub = rospy.Subscriber('/move_base/NavfnROS', Path, self.path_callback)
        self.waypoints = []
        self.mavlink_waypoints = []
        self.mav_connection = mavutil.mavlink_connection('udpin:localhost:14550')


    def path_callback(self, msg):
        self.waypoints = [(pose.pose.position.x, pose.pose.position.y) for pose in msg.poses]
        rospy.loginfo("Received path with {} waypoints".format(len(self.waypoints)))
        print("Received path with {} waypoints".format(len(self.waypoints)))
        
        self.mavlink_waypoints = convert_to_mavlink_waypoints(self.waypoints)
        for wp in self.mavlink_waypoints:
            self.mav_connection.mav.send(wp)
            print("waypoint sent")
    
    def get_waypoints(self):
        return self.waypoints



from pymavlink import mavutil



mav_connection = mavutil.mavlink_connection('udpin:localhost:14550')


if __name__ == "__main__":
    path_subscriber = PathSubscriber()
    rospy.spin