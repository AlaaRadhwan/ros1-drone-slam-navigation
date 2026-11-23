#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import GlobalPositionTarget

class RVIZNavGoalPublisher:
    def __init__(self):
        rospy.init_node('rviz_nav_goal_publisher')
        self.nav_goal_pub = rospy.Publisher('/mavros/setpoint_position/global', GlobalPositionTarget, queue_size=10)
        self.rviz_nav_goal_sub = rospy.Subscriber('/move_base_simple/goal', PoseStamped, self.rviz_nav_goal_callback)

    def rviz_nav_goal_callback(self, msg):
        # Convert the PoseStamped message to a GlobalPositionTarget message
        nav_goal = GlobalPositionTarget()
        nav_goal.latitude = msg.pose.position.x
        nav_goal.longitude = msg.pose.position.y
        nav_goal.altitude = msg.pose.position.z
        # Publish the navigation goal to the Mavlink topic
        self.nav_goal_pub.publish(nav_goal)

if __name__ == '__main__':
    try:
        RVIZNavGoalPublisher()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass