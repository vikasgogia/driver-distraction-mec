import cv2
import requests
import os
import uuid
import threading
import base64
from utils.constants import *
from utils.util import *
from flask import Flask, request, render_template
from signalsdk.signal_app import SignalApp
from CameraConnectorConfig import CameraConnectorConfig
from werkzeug.utils import secure_filename

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
# signalApp.initialize(onConfigChange, None)
camera = cv2.VideoCapture(config.cameraEndpoint)

queue_size_local = 0
processing_time_local = 0

queue_size_remote = 0
processing_time_remote = 0

lock_1 = threading.Lock()
lock_2 = threading.Lock()

@app.route('/update-local', methods=['POST'])
def update_data_1():
    global queue_size_local, processing_time_local
    data = request.json
    with lock_1:
        queue_size_local = data.get('queue_size', 0)
        processing_time_local = data.get('estimated_processing_time', 0)
    return jsonify(success=True)

@app.route('/update-remote', methods=['POST'])
def update_data_2():
    global queue_size_remote, processing_time_remote
    data = request.json
    with lock_2:
        queue_size_remote = data.get('queue_size', 0)
        processing_time_remote = data.get('estimated_processing_time', 0)
    return jsonify(success=True)

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

    try:
        response = requests.post(f'{config.localExecutorEndpoint}/upload1', files=frames)
        response.raise_for_status()
        
        response_data = response.json()
        proc_time_per_frame = response_data.get("proctime") / len(frames)
        return generateResponse(Constants.SUCCESS_KEY, f"Proc time per frame: {proc_time_per_frame}"), 200

    except requests.exceptions.RequestException as e:
        return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400

@app.route('/receive-task', methods=["POST"])
def rec_task():
    for idx, image in request.files.items():
        image_bytes = image.read()
        img_bytes = base64.b64decode(image_bytes)
        filename = secure_filename(f"imageToSave_{idx}.jpeg")
        with open(os.path.join(r'C:\Users\vikas\Downloads\driver-distraction-mec\meta', filename), "wb") as fh:
            fh.write(img_bytes)
    return jsonify({'message': 'Image saved successfully'})

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

        frames[f'image_{i}'] = ("captured_image.jpg", image_data.tobytes(), "image/jpeg")
    try:
        # task_id = uuid.uuid4()
        # tasks[task_id] = True
        response = requests.post(f'{config.localExecutorEndpoint}/task-upload', files=frames)
        response.raise_for_status()
        return generateResponse(Constants.SUCCESS_KEY, f"Pass"), 200
    except requests.exceptions.RequestException as e:
        return generateResponse(Constants.FAIL_KEY, f"Issue with sending the image - {e}."), 400
    
def make_decision():
    global queue_size_local, processing_time_local, queue_size_remote, processing_time_remote
    with lock_1, lock_2:
        if queue_size_local*processing_time_local > queue_size_remote*processing_time_remote:
            decision = "remote"
        else:
            decision = "local"
        return decision
    
if __name__ == "__main__":
    app.run( host="0.0.0.0", port=3000, threaded=True)
