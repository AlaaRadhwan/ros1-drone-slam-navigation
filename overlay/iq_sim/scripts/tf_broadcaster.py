#!/usr/bin/env python

import rospy
import tf
from gazebo_msgs.msg import ModelStates

def handle_model_pose(msg):
    br = tf.TransformBroadcaster()
    try:
        idx = msg.name.index('drone_with_lidar_camera')
        pose = msg.pose[idx]

        current_time = rospy.Time.now()
        # Broadcast transform from base_link to world
        br.sendTransform((pose.position.x, pose.position.y, pose.position.z),
                         (pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w),
                         current_time,
                         "base_link",
                         "odom")

        # Transform for hokuyo_link
        hokuyo_translation = (0, 0, 0.3)
        hokuyo_rotation = tf.transformations.quaternion_from_euler(0, 0, 0)
        br.sendTransform(hokuyo_translation,
                         hokuyo_rotation,
                         current_time,
                         "hokuyo_link",
                         "base_link")

        # Transform for hokuyo_sensor_link
        lidar_translation = (0, 0, 0.3)
        lidar_rotation = tf.transformations.quaternion_from_euler(0, 0, 1.57)
        br.sendTransform(lidar_translation,
                         lidar_rotation,
                         current_time,
                         "hokuyo_sensor_link",
                         "hokuyo_link")
    except ValueError:
        pass

if __name__ == '__main__':
    rospy.init_node('tf_broadcaster')
    rate = rospy.Rate(20)
    rospy.Subscriber('/gazebo/model_states', ModelStates, handle_model_pose)
    while not rospy.is_shutdown():
        rate.sleep()
    rospy.spin()

