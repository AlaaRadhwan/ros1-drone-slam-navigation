#!/bin/bash


if [ $# -eq 0 ]; then
    echo "Usage: $0 [launch_flask]"
    echo "Example: $0 true"
    exit 1
fi

launch_flask_server() {
    echo "Running flask server"
    gnome-terminal --tab -- bash -c "python3 drone_website/Server3.0/server_apps/main_app.py"
}


echo "Launching gazebo simulation"
gnome-terminal --tab -- bash -c "roslaunch iq_sim walls.launch; exec bash"


echo "Running startsitl.sh"
gnome-terminal --tab -- bash -c  "~/startsitl.sh; echo 'startsitl.sh is up'; exec bash"

echo "Running gmapping.launch"
gnome-terminal --tab -- bash -c "roslaunch iq_sim gmapping.launch; exec bash"

echo "Running tf_broadcaster.py"
gnome-terminal --tab -- bash -c "rosrun iq_sim tf_broadcaster.py; exec bash"

echo "Running rviz_goal_nav_publisher.py"
gnome-terminal --tab -- bash -c "rosrun iq_sim rviz_nav_goal_publisher.py; exec bash"

echo "Running rviz"
gnome-terminal --tab -- bash -c "rviz; exec bash"

# Check if the argument is true, then launch Flask server
if [ "$1" == "true" ]; then
    launch_flask_server
fi

# Launch flask server Server2.0

# echo "Running flask server"
# gnome-terminal --tab -- bash -c "python3 drone_website/Server2.0/server_apps/main_app.py "