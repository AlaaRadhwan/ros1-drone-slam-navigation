from flask import Blueprint, Response
import cv2
from cv_bridge import CvBridge


camera_bp = Blueprint('camera_process', __name__, template_folder="templates", static_folder="static")


bridge = CvBridge()
latest_image = None

# Call images from drone
def image_callback(msg):
    global latest_image
    latest_image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")


# Generate the image to be sent to the page
def generate():
    global latest_image
    while True:
        if latest_image is not None:
            resized_image = cv2.resize(latest_image, (640, 480))
            resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            _, jpeg = cv2.imencode('.jpg', resized_image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            


@camera_bp.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')