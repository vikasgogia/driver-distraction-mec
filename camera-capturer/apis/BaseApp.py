import cv2
import requests
import os
import uuid
import time
import threading
import random
import base64
from utils.constants import *
from utils.util import *
from flask import Flask, request, render_template
from signalsdk.signal_app import SignalApp
from CameraConnectorConfig import CameraConnectorConfig
from werkzeug.utils import secure_filename

class BaseApp():

    def __init__(self):
        self.config = CameraConnectorConfig()
        self.app = self.create_app()
        self.camera = cv2.VideoCapture(self.config.cameraEndpoint)

    def create_app(self):
        '''
            Initiating Flask app
        '''
        app = Flask(__name__)
        app.secret_key = self.__config.secretKey
        return app
    
    @app.route('/receive-task', methods=["POST"])
    def rec_task():
        for idx, image in request.files.items():
            image_bytes = image.read()
            img_bytes = base64.b64decode(image_bytes)
            filename = secure_filename(f"imageToSave_{idx}.jpeg")
            with open(os.path.join(r'C:\Users\vikas\Downloads\driver-distraction-mec\meta', filename), "wb") as fh:
                fh.write(img_bytes)
        return jsonify({'message': 'Image saved successfully'})