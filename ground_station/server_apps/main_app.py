from flask import Flask, render_template, jsonify
from flask import Response, request
from flask_socketio import SocketIO, emit

import os
import threading
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped

from apps.live_feed import camera_bp, image_callback
from apps.position_process import process_bp, update_drone_status
from apps.models import db, HomePosition
from apps.wasd_nav import *
# from apps.MessageQueue import UpdateDroneLocation
from apps.Send_path_drone import PathSubscriber

from nav_msgs.msg import Path


app = Flask(__name__, template_folder="../templates", static_folder="../static")
socketio =  SocketIO(app)

# PUBLIC-RELEASE EDIT: the archived source contained a hard-coded MySQL URI with a
# credential; it has been replaced by an environment variable. Example:
#   export DRONE_DB_URI='mysql://<user>:<password>@localhost:3306/drone_home_position'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DRONE_DB_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(camera_bp, url_prefix="")
app.register_blueprint(process_bp, url_prefix="")

db.init_app(app)

def return_initial_coord(coord_data):
    if coord_data:
        lat = coord_data.latitude
        lng = coord_data.longitude
    else:
        lat = -35.363263
        lng = 149.1652378
    
    return lat, lng

rospy.init_node('gazebo_camera_streamer', anonymous=True)


@app.route('/')
def index():
    return render_template('new_base.html')


@app.route('/navigation')
def navigation_page():

    takeoff_position = HomePosition.query.order_by(HomePosition.id.desc()).first()
    lat, lng = return_initial_coord(takeoff_position)
    return render_template('navigation_map.html', init_lat=lat, init_lng=lng)


@app.route('/graph')
def graph():
    return render_template('graph.html')


rospy.Subscriber('/webcam/image_raw', Image, image_callback)

def path_callback(msg):
    print("Received new path: ", len(msg.poses), " poses")

path_sub = rospy.Subscriber('/move_base/NavfnROS', Path, path_callback)


if __name__ == '__main__':
    
    drone_status_update_thread = threading.Thread(target=update_drone_status, daemon=True)
    drone_status_update_thread.start()
    app.run(debug=True)
    # socketio.run(app)
