# Edge Application Documentation

This documentation provides an overview of an Edge application designed for driver distraction detection, comprising various APIs and functionalities.

## Introduction

The Edge application utilizes a Flask-based server to interact with driver distraction detection AI services, both locally and remotely. It offers APIs for capturing images, analyzing processing time, receiving and sending tasks, recording data, and updating queue metadata.

## Components

### CameraConnectorConfig Class

- Manages configuration settings for camera endpoints and executor endpoints.
- Provides methods to set configuration settings.

### Flask App

- Initializes the Flask application.
- Defines routes for various functionalities.

### APIs

1. `/update-local`: Updates local queue metadata.
2. `/update-remote`: Updates remote queue metadata.
3. `/capture`: Captures images and sends them to the AI server for analysis.
4. `/proctime`: Captures frames from a video and analyzes processing time.
5. `/receive-task`: Receives tasks (images) for processing.
6. `/send-task`: Sends tasks (images) for processing.
7. `/record`: Records data and verifies the success of the recording.

### Helper Functions

- `make_decision()`: Makes a decision to select between local and remote processing based on queue metadata.
- `update_qsize_local()`: Fetches local queue metadata.
- `update_qsize_remote()`: Fetches remote queue metadata.
- `start_threading()`: Initiates threads for updating queue data.

## Usage

1. Start the Flask server.
2. Access the defined APIs to perform various tasks related to driver distraction detection.
3. Monitor the application for successful processing and data recording.

## Dependencies

- OpenCV (`cv2`)
- Requests (`requests`)
- Flask (`Flask`)
- Werkzeug (`werkzeug`)
- Base64 (`base64`)

## Configuration

- Ensure proper configuration settings are provided in the `CameraConnectorConfig` class.

## Additional Notes

- The application utilizes threading for concurrent updates of queue metadata.
- Error handling is implemented for robustness in API requests and data processing.