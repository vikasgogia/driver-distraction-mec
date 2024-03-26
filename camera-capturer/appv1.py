import cv2
import requests
import os
import time
import uuid
import threading
import time
import base64

from utils.constants import *
from utils.util import *

from flask import Flask, request, render_template
# from flask_socketio import SocketIO, emit
# import socketio
from flask_socketio import SocketIO
from signalsdk.signal_app import SignalApp
from CameraConnectorConfig import CameraConnectorConfig

camera = None

def create_app():
    '''
        Initiating Flask app
    '''
    app = Flask(__name__)
    app.secret_key = config.secretKey
    return app

def onConfigChange(arg_config):
    '''
        EdgeSignal SDK callback: triggered on config change e.g. updating settings
    '''
    global camera
    print("onConfigChange")
    config.setConfig(arg_config)
    camera = cv2.VideoCapture(config.cameraEndpoint)
    print("config = ", config)
    if(config == None):
        print("no config passed")

config = CameraConnectorConfig()
# os.environ[Constants.APPLICATION_ID] = config.appId
# signalApp = SignalApp()
app = create_app()
socketio = SocketIO(app)
# client = Client()
# signalApp.initialize(onConfigChange, None)
camera = cv2.VideoCapture(config.cameraEndpoint)

@app.route('/', methods=["GET"])
def ping():
    '''
        API to ping and verify the working of this application
    '''
    return render_template('index.html')

@app.route('/capture', methods=["POST"])
def capture_image():
    '''
        API to capture images and send to driver distraction detection AI server (localhost/ remote)
    '''
    if not request.method == "POST":
        return generateResponse(Constants.ERROR_KEY, "Only POST requests are allowed."), 400
    
    ret, frame = camera.read()
    if not ret:
        return generateResponse(Constants.ERROR_KEY, "Failed to capture an image."), 400

    try:
        _, image_data = cv2.imencode(Constants.JPG, frame)
        files = { Constants.IMAGE: (f"captured_image{Constants.JPG}", image_data.tobytes(), "image/jpeg") }
        response = requests.post(f'{config.localExecutorEndpoint}/upload', files=files)
        response.raise_for_status()
        # return generateResponse(Constants.SUCCESS_KEY, "Image sent."), 200
        response_data = response.json()
        output = response_data.get("output", "")
        annotated_image_b64 = response_data.get("annotated_image", "")

        return render_template('index.html', output=output, annotated_image_b64=annotated_image_b64)

    except requests.exceptions.RequestException as e:
        return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400

@app.route('/proctime', methods=["POST"])
def proc_time():
    '''
        API to capture frames from a video and send to driver distraction detection AI server (localhost/ remote) to analyse time required for each frame
    '''
    if not request.method == "POST":
        return generateResponse(Constants.ERROR_KEY, "Only POST requests are allowed."), 400
    
    video_path = r'C:\Users\vikas\Downloads\project_uottawa\driver-distraction-mec\meta\vid.mp4'
    cap = cv2.VideoCapture(video_path)

    frames = {}
    num_frames_to_capture = 60
    for i in range(num_frames_to_capture):
        ret, frame = cap.read()
        if not ret:
            return generateResponse(Constants.ERROR_KEY, "Failed to capture an image."), 400
        _, image_data = cv2.imencode(Constants.JPG, frame)
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        frames[f'image_{i}'] = image_data_base64
        # frames[f'image_{i}'] = ("captured_image.jpg", image_data.tobytes(), "image/jpeg")
        # frames.append(('image', ("captured_image.jpg", image_data.tobytes(), "image/jpeg")))

    try:
        response = requests.post(f'{config.localExecutorEndpoint}/upload1', files=frames)
        response.raise_for_status()
        
        response_data = response.json()
        # output = response_data.get("output", "")
        proc_time_per_frame = response_data.get("proctime") / len(frames)
        # annotated_image_b64 = response_data.get("annotated_image", "")

        return generateResponse(Constants.SUCCESS_KEY, f"Proc time per frame: {proc_time_per_frame}"), 200

    except requests.exceptions.RequestException as e:
        return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400
    
    
    



# socketio = SocketIO(app)
# websocket_urls = {
#     'local': 'http://localhost:5001/',
#     'remote': 'http://localhost:5002/'
# }

# Create first SocketIO client and connect to the first server
# sio1 = socketio.Client()
# sio1.connect('http://localhost:5001')

# Define event handlers for the first client
# @sio1.event
# def connect():
#     print('Connected to first server')

# @sio1.event
# def disconnect():
#     print('Disconnected from first server')

# @sio1.on('processed-task')  
# def handle_server_message(message):
#     print('Received message from first server:', message)

# # Create second SocketIO client and connect to the second server
# sio2 = socketio.Client()
# sio2.connect('http://<server_ip2>:5000')

# # Define event handlers for the second client
# @sio2.event
# def connect():
#     print('Connected to second server')

# @sio2.event
# def disconnect():
#     print('Disconnected from second server')

# @sio2.on('server_message')  
# def handle_server_message(message):
#     print('Received message from second server:', message)

# # Keep the clients running
# sio1.wait()
# sio2.wait()

socket_clients = {}
tasks = {}
# for key, url in websocket_urls.items():
#     socket_clients[key] = SocketIO(app, logger=True, async_mode='threading', engineio_logger=True, async_handlers=True)
#     # socket_clients[key].connect(url)


# @socketio.on('processed-task')
# def fetch_processed_task(data):
#     print(data)

@app.route('/send-task', methods=["POST"])
def send_task():
    '''
        API
    '''
    if not request.method == "POST":
        return generateResponse(Constants.ERROR_KEY, "Only POST requests are allowed."), 400
    video_path = r'C:\Users\vikas\Downloads\driver-distraction-mec\meta\vid.mp4'
    cap = cv2.VideoCapture(video_path)
    frames = {}
    num_frames_to_capture = 60
    for i in range(num_frames_to_capture):
        ret, frame = cap.read()
        if not ret:
            return generateResponse(Constants.ERROR_KEY, "Failed to capture an image."), 400
        _, image_data = cv2.imencode(Constants.JPG, frame)
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        frames[f'image_{i}'] = image_data_base64
    try:
        # url = decision(frames)
        # server_key = 'local'
        task_id = uuid.uuid4()
        tasks[task_id] = True
        print(f"emitting task: {task_id}")
        # frames_json_serializable = frames.decode('utf-8')  # Decode bytes to string
        # websocket_thread = threading.Thread(target=run_websocket_client, args=({'task_id': str(task_id), 'frames': frames},))
        # websocket_thread.start()
        # sio1.emit('task', {'task_id': str(task_id), 'frames': frames})
        # run_websocket_client({'task_id': str(task_id), 'frames': frames})
        # sio1.emit('task', {'task_id': str(task_id), 'frames': frames})
        socketio.emit('api_data', {'task_id': str(task_id), 'frames': frames})
        return generateResponse(Constants.SUCCESS_KEY, f"Pass"), 200

    except requests.exceptions.RequestException as e:
        return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400


# def send_task1():
#     video_path = r'C:\Users\vikas\Downloads\driver-distraction-mec\meta\vid.mp4'
#     cap = cv2.VideoCapture(video_path)
#     frames = {}
#     num_frames_to_capture = 60
#     for i in range(num_frames_to_capture):
#         ret, frame = cap.read()
#         _, image_data = cv2.imencode(Constants.JPG, frame)
#         image_data_base64 = base64.b64encode(image_data).decode('utf-8')
#         frames[f'image_{i}'] = image_data_base64
#     try:
#         task_id = uuid.uuid4()
#         tasks[task_id] = True
#         print(f"emitting task: {task_id}")
#         sio1.emit('task', {'task_id': str(task_id), 'frames': frames})
#         # run_websocket_client({'task_id': str(task_id), 'frames': frames})
#         sio1.emit('task', {'task_id': str(task_id), 'frames': frames})
#         return generateResponse(Constants.FAIL_KEY, f"Pass"), 200

#     except requests.exceptions.RequestException as e:
#         return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400

# # Function to run the WebSocket client
# def run_websocket_client():
#     print("connecting to socket connection")
#     sio1.connect('http://localhost:5001')
#     # sio1.emit('task', data)
#     # sio1.wait()
    
def run_app():
    app.run(host="0.0.0.0", port=3000, threaded=True)
    
if __name__ == "__main__":
    # websocket_thread = threading.Thread(target=run_app)
    # websocket_thread.start()
    
    socketio.run(app, host="0.0.0.0", port=3000)