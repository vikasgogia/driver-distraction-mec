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
import socketio
from signalsdk.signal_app import SignalApp
from CameraConnectorConfig import CameraConnectorConfig

@sio1.event
def connect():
    print('Connected to first server')

@sio1.event
def disconnect():
    print('Disconnected from first server')

@sio1.on('processed-task')  
def handle_server_message(message):
    print('Received message from first server:', message)