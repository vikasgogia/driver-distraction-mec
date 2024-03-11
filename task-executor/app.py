import argparse
import base64
import io
import os
import torch
import time
import numpy as np

from yolov5.yolo_api import *

from PIL import Image, ImageDraw
from flask import Flask, request, jsonify, render_template

ERROR_KEY = "error"
SUCCESS_KEY = "success"

app = Flask(__name__)

def save_annotated_image(image, results, save_path):
    draw = ImageDraw.Draw(image)
    for result in results:
        # Assuming keys for bounding box coordinates are 'xmin', 'ymin', 'xmax', 'ymax'
        xmin, ymin, xmax, ymax = result['xmin'], result['ymin'], result['xmax'], result['ymax']
        confidence, _, name = result['confidence'], result['class'], result['name']

        draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)
        label = f"{name} ({confidence:.2f})"
        draw.text((xmin, ymin - 10), label, fill="red")
        
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    annotated_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return annotated_image_base64
    
@app.route('/', methods=['GET'])
def hello():
    return '<h1>Hello from Docker</h2>'

@app.route('/upload', methods=['POST'])
def upload_image():
    if not request.method == "POST":
        return jsonify({ERROR_KEY: "Only POST requests are allowed"}), 400
    
    if 'image' not in request.files or not request.files['image'].filename:
        return jsonify({ERROR_KEY: 'No image in the request'}), 400

    image = request.files['image']
    try:
        image_bytes = image.read()
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        return jsonify({ERROR_KEY: f"Error processing image: {str(e)}"}), 500

    try:
        results = model(img, size=640)  # reduce size=320 for faster inference
        save_path = os.path.join('uploads', 'annotated_' + image.filename)
        img_b64 = save_annotated_image(img.copy(), results.pandas().xyxy[0].to_dict(orient="records"), save_path)
        
        return jsonify({"annotated_image": img_b64}), 200
    
    except Exception as e:
        print(str(e))
        return jsonify({ERROR_KEY: f"Error predicting: {str(e)}"}), 500
    
@app.route('/upload1', methods=['POST'])
def upload_image1():
    start_time = time.time()
    if not request.method == "POST":
        return jsonify({ERROR_KEY: "Only POST requests are allowed"}), 400
    
    if not request.files:
        return jsonify({ERROR_KEY: 'No image in the request'}), 400

    annotated_imgs = {}
    for key, val in request.files.items():
        image = val
        try:
            image_bytes = image.read()
            img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return jsonify({ERROR_KEY: f"Error processing image: {str(e)}"}), 500

        try:
            results = model(img, size=640)  # reduce size=320 for faster inference
            save_path = os.path.join('uploads', 'annotated_' + image.filename)
            img_b64 = save_annotated_image(img.copy(), results.pandas().xyxy[0].to_dict(orient="records"), save_path)
            annotated_imgs[f"annotated_{key}"] = img_b64
        
        except Exception as e:
            print(str(e))
            return jsonify({ERROR_KEY: f"Error predicting: {str(e)}"}), 500
    
    end_time = time.time()
    return jsonify({"annotated": annotated_imgs, "proctime": end_time-start_time}), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Flask API exposing YOLOv5 model")
    parser.add_argument("--port", default=5000, type=int, help="Port number")
    parser.add_argument('--model', default='yolov5s', help='Model to run, i.e. --model yolov5s')
    args = parser.parse_args()

    try:
        os.makedirs('uploads', exist_ok=True)
        model = torch.hub.load('ultralytics/yolov5', args.model)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        exit(1)
    app.run(host='0.0.0.0', port=5001, threaded=True)
