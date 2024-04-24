# Executor Application Documentation

This documentation provides an overview of the Executor application designed for processing images and tasks using YOLOv5 model.

## Introduction

The Executor application processes image and task data received via APIs. It utilizes YOLOv5 model for image processing and Scheduler for task scheduling.

## Components

### ImgProcessor Class

- Initializes and manages YOLOv5 model for image processing.
- Provides methods for image processing and annotating.

### Task Class

- Represents a task with a unique identifier, images, annotated images, and timing information.

### Scheduler Class

- Manages task scheduling based on chosen scheduling algorithm (FCFS or SJF).
- Processes tasks concurrently and records performance metrics.

### Flask App

- Initializes the Flask application.
- Defines routes for uploading images, tasks, and retrieving queue metadata.

## Usage

1. Start the Flask server.
2. Access the defined APIs to upload images and tasks for processing.
3. Monitor the application for task scheduling and performance metrics.

## APIs

1. `/upload`: Uploads single images for processing.
2. `/upload1`: Uploads multiple images for batch processing.
3. `/task-upload`: Uploads tasks for processing.
4. `/queue-metadata`: Retrieves queue metadata.
5. `/record`: Records performance metrics before shutdown.

## Dependencies

- PyTorch
- TorchVision
- Ultralytics YOLOv5
- Flask
- Requests
- PIL

## Additional Notes

- The application supports both single and batch image processing.
- Task scheduling is based on either First-Come-First-Served (FCFS) or Shortest Job First (SJF) algorithms.
- Performance metrics include average waiting time, processing time, size of tasks, and drop ratio.

