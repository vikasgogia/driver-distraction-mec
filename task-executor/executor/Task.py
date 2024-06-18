# import uuid
import time

class Task():
    
    def __init__(self, id, task_id, images):
        self.id = id
        self.task_id = task_id
        self.images = images
        self.annotated_images = {}
        self.start_wait = time.time()
        self.end_wait = time.time()
        self.arrival_time = time.time()
        self.deadline = self.arrival_time + 180
        self.expected_processing_time = 20 * (len(images) / (120))
    
    def __lt__(self, other):
        # Define your comparison logic here. For example, comparing the number of images:
        return len(self.images) < len(other.images)