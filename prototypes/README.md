# Prototypes

`send_test.py` is an early experiment that subscribed to `/move_base/NavfnROS` and sent MAVLink waypoints directly. It was superseded by `overlay/iq_sim/scripts/navigation_test.py`. It is kept unmodified for history and is known to be incomplete (e.g. `rospy.spin` is not called, and a MAVLink connection is opened twice). An even earlier fragment (`another_send_test.py`, syntactically truncated) was omitted.
