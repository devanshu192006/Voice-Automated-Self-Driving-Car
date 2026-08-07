import os
import sys
import socket
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import socketio
import eventlet
from flask import Flask
from tensorflow.keras.models import load_model

# Import voice controller module
import voice_control

# Hide TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Initialize SocketIO server and Flask app
sio = socketio.Server()
app = Flask(__name__)

def preprocess_image(img):
    img = img[60:135, :, :]
    img = cv2.resize(img, (200, 66))
    img = img / 255.0 
    return img

@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        speed = float(data["speed"])
        
        # Decode image from simulator
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        
        # Preprocess image
        processed_img = preprocess_image(image)
        image_input = np.array([processed_img])
        
        # Predict steering angle via deep learning model
        prediction = model.predict(image_input, batch_size=1, verbose=0)
        ai_steering_angle = float(np.squeeze(prediction))
        
        # Get active command from background voice listener
        command = voice_control.current_command
        
        steering_angle = 0.0
        throttle = 0.0

        if command == "forward":
            # AI steering + Cruise Control targeting 40 mph
            steering_angle = ai_steering_angle
            target_speed = 40.0
            throttle = (target_speed - speed) * 0.1
            throttle = max(-1.0, min(throttle, 1.0))

        elif command == "left":
            steering_angle = -0.5
            throttle = 0.2

        elif command == "right":
            steering_angle = 0.5
            throttle = 0.2

        elif command == "backward":
            steering_angle = 0.0
            throttle = -0.4

        elif command == "stop":
            steering_angle = 0.0
            throttle = -1.0 if speed > 1.0 else 0.0  # Apply brakes until stationary

        print(f"Command: {command.upper()} | Steering: {steering_angle:.3f} | Throttle: {throttle:.3f} | Speed: {speed:.3f}")
        send_control(steering_angle, throttle)
    else:
        sio.emit('manual', data={}, skip_sid=True)

@sio.on('connect')
def connect(sid, environ):
    print("Simulator Connected successfully!", sid)
    send_control(0, 0)

def send_control(steering_angle, throttle):
    sio.emit(
        'steer',
        data={
            'steering_angle': str(steering_angle),
            'throttle': str(throttle)
        },
        skip_sid=True)

def find_free_port(start_port=4567, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('', port))
                return port
            except OSError:
                continue
    raise OSError(f"No free port available between {start_port} and {start_port + max_attempts - 1}.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide the model file name. Example: python drive.py model.h5")
        sys.exit()

    model_path = sys.argv[1]
    requested_port = int(sys.argv[2]) if len(sys.argv) > 2 else 4567

    print(f"Loading model: {model_path}...")
    model = load_model(model_path, compile=False)

    # Start Voice Control Thread
    voice_control.start_voice_thread()

    app = socketio.WSGIApp(sio, app)

    try:
        port = find_free_port(requested_port)
    except OSError as exc:
        print(f"Unable to start the simulator server: {exc}")
        sys.exit(1)

    if port != requested_port:
        print(f"Port {requested_port} is already in use. Using port {port} instead.")
    else:
        print(f"Starting server on port {port}... Waiting for simulator connection.")

    eventlet.wsgi.server(eventlet.listen(('', port)), app)