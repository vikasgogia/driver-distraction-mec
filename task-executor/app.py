import time
import signal
import pandas as pd
from executor.ImgProcessor import *
from executor.Task import *
from scheduler.genetic.GeneticScheduler import GeneticScheduler
from scheduler.milp.MILPAlgorithm import MILPAlgorithm
# from scheduler.OptimizationScheduler import OptimizationScheduler
from scheduler.Scheduler import *
from flask import Flask, request, jsonify

ERROR_KEY = "error"
SUCCESS_KEY = "success"
app = Flask(__name__)
    
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
        # results = model(img, size=640)  # reduce size=320 for faster inference
        # save_path = os.path.join('uploads', 'annotated_' + image.filename)
        # img_b64 = save_annotated_image(img.copy(), results.pandas().xyxy[0].to_dict(orient="records"), save_path)
        
        # return jsonify({"annotated_image": img_b64}), 200
        return jsonify({"Success": "Pass"})    
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
            # results = model(img, size=640)  # reduce size=320 for faster inference
            # save_path = os.path.join('uploads', 'annotated_' + image.filename)
            # img_b64 = save_annotated_image(img.copy(), results.pandas().xyxy[0].to_dict(orient="records"), save_path)
            # annotated_imgs[f"annotated_{key}"] = img_b64
            return jsonify({"Success": "Pass"})   
        except Exception as e:
            print(str(e))
            return jsonify({ERROR_KEY: f"Error predicting: {str(e)}"}), 500
    
    end_time = time.time()
    return jsonify({"annotated": annotated_imgs, "proctime": end_time-start_time}), 200



@app.route('/task-upload', methods=['POST'])
def upload_task():
    start_time = time.time()
    
    if not request.method == "POST":
        return jsonify({ERROR_KEY: "Only POST requests are allowed"}), 400
    
    if not request.files:
        return jsonify({ERROR_KEY: 'No image in the request'}), 400

    images = []
    for _, image in request.files.items():
        try:
            image_bytes = image.read()
            bytes_io = io.BytesIO(image_bytes)
            images.append(bytes_io)
        except Exception as e:
            print(e)

    task = Task(id=request.remote_addr, images=images)
    task_scheduler.submit_task(task)
    end_time = time.time()
    return jsonify({"proctime": (end_time - start_time)}), 200




@app.route('/queue-metadata', methods=['POST'])
def queue_metadata():
    # TODO: incorporate logic for avergae processing time
    qsize = task_scheduler.get_queue_size()
    return jsonify({'qsize': qsize})


@app.route('/record', methods=['GET'])
def record():
    try:
        print("request received")
        cleanup_before_shutdown()
        return 'success'
    except Exception as e:
        return f'{e}'

def cleanup_before_shutdown():
    print("Performing clean-up tasks before shutdown...")
    task_scheduler.record_run()
    print("Clean-up complete.")

# Register the clean-up function for SIGINT and SIGTERM signals
def handle_termination_signal(signal_number=None, frame=None):
    # cleanup_before_shutdown()
    task_scheduler.record_run()
    task_scheduler.df.to_csv('record_remote.csv', index=False)
    exit(0)  # Exit the program with code 0 (success)

# Register the termination signal handler
signal.signal(signal.SIGINT, handle_termination_signal)
signal.signal(signal.SIGTERM, handle_termination_signal)

if __name__ == '__main__':
    # task_scheduler = Scheduler(Scheduler.Scheduling.SJF)

    # initialize genetic scheduler
    task_scheduler = GeneticScheduler()
    try:
        task_scheduler.init()
    except Exception as e:
        exit(1)

    app.run(host='0.0.0.0', port=5002, threaded=True)