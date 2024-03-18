import uuid

class Task():
    
    def __init__(self, images):
        self.id = uuid.uuid4()
        self.images = images
        self.annotated_images = {}