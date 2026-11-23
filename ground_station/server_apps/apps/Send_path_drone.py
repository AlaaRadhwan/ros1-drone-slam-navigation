import rospy
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

class PathSubscriber:
    def __init__(self):
        # rospy.init_node("path_subscriber", anonymous=True)
        self.path_sub = rospy.Subscriber('/move_base/NavfnROS', Path, self.path_callback)
        self.waypoints = []

    def path_callback(self, msg):
        self.waypoints = [(pose.pose.position.x, pose.pose.position.y) for pose in msg.poses]
        rospy.loginfo("Received path with {} waypoints".format(len(self.waypoints)))
        print("Received path with {} waypoints".format(len(self.waypoints)))
    
    def get_waypoints(self):
        return self.waypoints



if __name__ == "__main__":
    path_subscriber = PathSubscriber()
    rospy.spin