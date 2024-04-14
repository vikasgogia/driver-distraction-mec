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