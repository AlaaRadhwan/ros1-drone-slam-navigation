from flask import Blueprint, redirect, url_for, request, jsonify
from pymavlink import mavutil
import time
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
import threading
from apps import control_functions, return_to_launch
from apps.models import db, HomePosition
from apps.wasd_nav import *
from apps.MessageQueue import MessageQueue
from apps.Send_path_drone import PathSubscriber

from mavros_msgs.msg import GlobalPositionTarget
from geometry_msgs.msg import TransformStamped
import tf2_geometry_msgs
import tf2_ros
import rospy

process_bp = Blueprint('position_process', __name__, template_folder="templates", static_folder='static')

mav_connection = mavutil.mavlink_connection('udpin:localhost:14550')

lock = threading.Lock()
another_lock = threading.Lock()

message_queue = MessageQueue(another_lock, mav_connection)

updated_pos = [0, 0, 0]
updated_yaw = [0, 0, 0, 1]

drone_coordinates = {'lat': 0.0, 'lng': 0.0, 'alt': 0.0}
# home_coordinates = {'lat': 0.0, 'lng': 0.0, 'alt': 0.0}
takeoff_coordinates = {}

drone_status = 'landed'
connected = False
gps_locked = False

home_left = False

uScore = 50
score = 20

# --------------------------------
# Save Home to Database:
# --------------------------------

def save_takeoff_to_db(takeoff_coordinates):
    existing_takeoff_position = HomePosition.query.first()
    
    if existing_takeoff_position is None or \
            (takeoff_coordinates['lat'] != existing_takeoff_position.latitude or
            takeoff_coordinates['lng'] != existing_takeoff_position.longitude or
            takeoff_coordinates['alt'] != existing_takeoff_position.altitude):
        
        # print("Adding new coordinates to database...")
        home_position = HomePosition(latitude=Decimal(takeoff_coordinates['lat']),
                                    longitude=Decimal(takeoff_coordinates['lng']),
                                    altitude=Decimal(takeoff_coordinates['alt']))
        db.session.add(home_position)
        db.session.commit()
        # print(f"The new values add: {home_position.latitude}, {home_position.longitude}")


# --------------------------------
# Update drones lat and lng
# --------------------------------

def update_drone_status():
    global drone_status, connected, gps_locked, drone_coordinates
    while True:
        with lock:
            msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
            if msg:
                connected = True
                if msg.system_status == mavutil.mavlink.MAV_STATE_ACTIVE:
                    drone_status = 'in_flight'
                else:
                    drone_status = 'landed'
                
            
            gps_msg = mav_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if gps_msg:
                # Convert coordinates from 1e7 scale to degrees
                drone_coordinates = {
                    'lat': gps_msg.lat / 1e7,
                    'lng': gps_msg.lon / 1e7,
                    'alt': gps_msg.alt / 1e3 # Convert altitude from millimeters to meters
                }

            updated_pos[0], updated_pos[1], updated_pos[2] = control_functions.NED_position(mav_connection, rounded=True, positiveZ=True)

        time.sleep(0.5)



# -------------------------------------------
# Process drones arm and disarm commands
# -------------------------------------------
        
@process_bp.route('/process_arm_disarm', methods=['POST'])
def precess_arm_disarm():
    if request.method == 'POST':
        action = request.form['action']

        print("="*uScore)
        print(f"{action} drone in progress...!")
        print('-'*score)

        # Set drone in GUIDED MODE
        # control_functions.set_mode(mav_connection, "GUIDED")

        commands = [
            ("SET_MODE", "GUIDED"),
        ]

        if action == 'arm':
            # control_functions.arm(mav_connection, 1)
            commands.append(("ARM", 1))
            for command, args in commands:
                message_queue.add_command(command, args)

        elif action == 'disarm':
            # control_functions.arm(mav_connection, 0)
            commands.append(("ARM", 0))

        message_queue.exeute_commands()
        print("Commands for disarm", commands)

            
        
    return jsonify({"message": 'arm command received'})


# -------------------------------------------
# Process drones takeoff, yaw, and altitude
# -------------------------------------------

@process_bp.route('/process_takeoff', methods=['POST'])
def process_takeoff():
    if request.method == 'POST':

        print("="*uScore)
        print("Takeoff Started...!")
        print('-'*score)

        alt = int(request.form.get('altitude')) if request.form.get("altitude") != "" else 1

        commands = [
            ("SET_MODE", "GUIDED"),
            ("ARM", 1),
            ("TAKEOFF", alt),
        ]

        with lock:
            for command, args in commands:
                message_queue.add_command(command, args)
        
            message_queue.exeute_commands()
            updated_pos[2] = alt

            takeoff_coordinates = control_functions.get_takeoff_position(mav_connection)
            save_takeoff_to_db(takeoff_coordinates)

        

    return jsonify({"message": 'Takeoff command received', 'altitude': alt})


@process_bp.route('/process_yaw', methods=['POST'])
def process_yaw():
    if request.method == 'POST':
        print("="*uScore)
        print("Yaw Recieved...!")
        print('-'*score)

        yaw = int(request.form.get('yaw')) if request.form.get("yaw") != "" else 1
        speed = int(request.form.get('yawSpeed')) if request.form.get("yawSpeed") != "" else 10

        with lock:

            # control_functions.yaw(mav_connection, [yaw, speed, 0, 0])
            message_queue.add_command("YAW", [yaw, speed, 0, 0])
            message_queue.exeute_commands()
            print("Updating yaw")
            updated_yaw[1] = yaw
            print("Yaw updated")
    
        return jsonify({"message": 'Yaw command received', 'Yaw:': yaw})



@process_bp.route('/process_altData', methods=['POST'])
def process_altData():
    if request.method == 'POST':
        print("="*uScore)
        print("Altitude Recieved...!")
        print('-'*score)

        action = request.form['action']
        alt_amount = float(request.form['alt_amount']) if request.form['alt_amount'] != "" else 1

        lat = drone_coordinates['lat']
        lon = drone_coordinates['lng']
        alt = drone_coordinates['alt']

        if action == 'increase':
            drone_coordinates['alt'] += alt_amount
            control_functions.global_movement(mav_connection, lat, lon, drone_coordinates['alt'])

        elif action == 'decrease':
            drone_coordinates['alt'] -= alt_amount
            control_functions.global_movement(mav_connection, lat, lon, drone_coordinates['alt'])


        print("after alt", drone_coordinates)

        speed = 1

        if action == 'forward':
            print("forward received, sending command")
            control_functions.send_global_velocity(mav_connection, lat, lon, alt, 0, speed, 0, 1)

        elif action == 'backward':
            print("forward received, sending command")
            control_functions.send_global_velocity(mav_connection, lat, lon, alt, 0, -speed, 0, 1)

        elif action == 'right':
            print("forward received, sending command")
            control_functions.send_global_velocity(mav_connection, lat, lon, alt, -speed, 0, 0, 1)

        elif action == 'left':
            print("forward received, sending command")
            control_functions.send_global_velocity(mav_connection, lat, lon, alt, speed, 0, 0, 1)
    return jsonify({"message": 'Alt command received', 'altitude': alt})


# -------------------------------------------
# Process Rviz 2D Navigation
# -------------------------------------------

@process_bp.route('/send_waypoints', methods=['POST'])
def send_waypoints():
    path_subscriber = PathSubscriber()
    waypoints = path_subscriber.get_waypoints()
    print(waypoints)
    if not waypoints:
        print("I don't see any waypoints")
    
    mavlink_waypoints = control_functions.convert_to_mavlink_waypoints(waypoints)
    wp_num = 0
    for wp in mavlink_waypoints:
        mav_connection.mav.send(wp)
        wp_num += 1
        print(f"Sending waypoint number: {wp_num}")

    return jsonify({"messaage": "Waypoints sent successfully"})

# --------------------------------
# Process drones land and rtl
# --------------------------------

@process_bp.route('/landing_process', methods=['POST'])
def button_pressed():

    data = request.json
    button_id = data.get('action')

    allowed_button_ids = ['land', 'rtl']
    if button_id not in allowed_button_ids:
        return "Invalid button_id"
    
    print("="*uScore)
    print("Landing...!")
    print("-"*score)

    with lock:
        if button_id == 'land':
            message_queue.add_command("LAND", False)
            message_queue.exeute_commands()
            updated_pos[2] = 0
            message = 'Landing command received'
        
        if button_id == 'rtl':
            message_queue.add_command("RTL")
            message_queue.exeute_commands()

            for i in range(len(updated_pos)):
                updated_pos[i] = 0
            message = "Return-To-Launch command received"

        else:
            message = 'Invalid action'

    return jsonify({'message': message})    


# --------------------------------
# Process drones XYZ position
# --------------------------------

@process_bp.route("/process_positions", methods=['POST'])
def process_positions():
    if request.method == 'POST':

        updated_pos[0] = int(request.form['x_pos']) if request.form['x_pos'] != '' else updated_pos[0]
        updated_pos[1] = int(request.form['y_pos']) if request.form['y_pos'] != '' else updated_pos[1]
        updated_pos[2] = int(request.form['z_pos']) if request.form['z_pos'] != '' else updated_pos[2]

        updated_yaw[0] = int(request.form['yaw_rot']) if request.form['yaw_rot'] != '' else updated_yaw[0]
        updated_yaw[1] = int(request.form['yaw_speed']) if request.form['yaw_speed'] != '' else updated_yaw[1]

        if 'yaw_cw' in request.form:
            checkbox_value = request.form['yaw_cw']
            updated_yaw[2] = -1 if checkbox_value == 'ccw' else 1

        else:
            updated_yaw[2] = 1

        if 'rel_or_abs' in request.form:
            
            checkbox_value = request.form['rel_or_abs']
            updated_yaw[3] = 1 if checkbox_value == 'rel' else 0
        else:
            updated_yaw[3] = 0

        print(f"updated positions: {updated_pos}")
        print(f'Updated yaw settings: {updated_yaw}')
        control_functions.movement(mav_connection, updated_pos)
        control_functions.yaw(mav_connection, updated_yaw)

    return redirect(url_for('navigation_page'))


# --------------------------------
# WASD navigation controll
# --------------------------------



# --------------------------------
# Send coord to droneMarker.js
# --------------------------------

@process_bp.route('/get_drone_coordinates')
def get_drone_coordinates():
    return jsonify(drone_coordinates)


# --------------------------------
# Send coord to graph.js
# --------------------------------

@process_bp.route('/receive_graph_coordinates')
def receive_graph_coordinates():
    return jsonify(drone_coordinates)

# --------------------------------
# Move drone to marker on map
# --------------------------------

@process_bp.route('/move_drone', methods=['POST'])
def move_drone():
    data = request.get_json()
    location = data.get('location')
    alt = drone_coordinates['alt']

    if location:
        lat, lon = location['lat'], location['lng']

        control_functions.global_movement(mav_connection, lat, lon, alt)
        # print(drone_coordinates)
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Location not provided")


# --------------------------------
# Process waypoints lists
# --------------------------------
    
# ----- Function to check Proximity: -----------
    
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Radius of the Earth in meters
    dlat = radians(lat2- lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2    
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance


@process_bp.route('/send_marker_list', methods=['POST'])
def send_marker_list():
    data = request.get_json()
    markers = data.get('markers', [])

    alt = drone_coordinates['alt']

    init_lat, init_lon = drone_coordinates['lat'], drone_coordinates['lng']

    proximity_threshold = 3

    locationId = 0
    done = False

    for location in markers:
        # locationId = 1
        # print("------------------------------")
        # print('This is location: ', location)
        target_lat, target_lon = location['lat'], location['lng']

        while True:
            current_lat, current_lon = drone_coordinates['lat'], drone_coordinates['lng']
            distance_to_target = haversine(current_lat, current_lon, target_lat, target_lon)
            
            # print("--- Distance to target: ", distance_to_target)

            if distance_to_target > proximity_threshold:

                control_functions.global_movement(mav_connection, target_lat, target_lon, alt)

                # print("-Drone Moving to location: ", locationId)
                # print(f"-target: {target_lat}, {target_lon}")
                # print(f"-current: {current_lat}, {current_lon}")
            
            elif distance_to_target <= proximity_threshold:
                # print("----------------------")
                # print("distance reached!")
                break

        locationId += 1

        if locationId == len(markers):
            done = True

    print(f"location id: {locationId}, Markers len: {len(markers)}")

    if done:
        print("------------------------")
        print("Done and returning to first position!")
        control_functions.global_movement(mav_connection, init_lat, init_lon, alt)

    return jsonify({'message': 'Marker list received successfully'})



