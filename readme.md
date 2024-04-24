# Driver Distraction Detection System

This project aims to develop a driver distraction detection system utilizing edge computing. It comprises several components including image processing, task scheduling, and performance monitoring.

## Components

### Executor Application

The Executor application is responsible for processing images and tasks using the YOLOv5 model. It includes the following components:

- `ImgProcessor`: Initializes and manages the YOLOv5 model for image processing. Provides methods for image processing and annotating.
- `Task`: Represents a task with images, annotated images, and timing information.
- `Scheduler`: Manages task scheduling based on chosen algorithms. Processes tasks concurrently and records performance metrics.
- Flask App: Initializes the Flask application and defines routes for uploading images, tasks, and retrieving queue metadata.

### CameraConnectorConfig

This module manages configuration settings for camera and executor endpoints.

### Test Script

The test script is designed to evaluate the performance of the system by making repeated API calls to submit tasks for processing. It includes the following features:

- Makes API calls to send tasks to the Executor application.
- Measures performance metrics such as waiting time and processing time.
- Utilizes the requests library for HTTP requests and time module for timing operations.

## Usage

1. Start the Executor application and ensure proper configuration settings are in place.
2. Run the test script to evaluate the system performance by simulating task submission.
3. Monitor the Executor application for task scheduling and processing.
4. Analyze performance metrics recorded by the Executor application.

## Dependencies

- PyTorch
- TorchVision
- Ultralytics YOLOv5
- Flask
- Requests
- PIL

## Conclusion

The driver distraction detection system leverages edge computing to efficiently process tasks and detect distractions in real-time. By combining image processing, task scheduling, and performance monitoring, the system aims to enhance driver safety and reduce the risk of accidents caused by distractions.