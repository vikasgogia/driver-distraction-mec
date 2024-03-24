from executor.Task import *
import argparse
import base64
import io
import torch
import logging
from PIL import Image, ImageDraw

class ImgProcessor():
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def init_yolo_model(self) -> bool:
        parser = argparse.ArgumentParser(description='YOLOv5 model')
        parser.add_argument('--model', default='yolov5s', help='YOLO model to run')
        args = parser.parse_args()

        try:
            # os.makedirs('uploads', exist_ok=True)
            self.__model = torch.hub.load('ultralytics/yolov5', args.model)
            return True
        except Exception as e:
            self.logger.error(f'Error loading model: {str(e)}')
            return False
    
    def __save_annotated_image(self, image, results):
        draw = ImageDraw.Draw(image)
        for result in results:
            xmin, ymin, xmax, ymax = result['xmin'], result['ymin'], result['xmax'], result['ymax']
            confidence, _, name = result['confidence'], result['class'], result['name']

            draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)
            label = f"{name} ({confidence:.2f})"
            draw.text((xmin, ymin - 10), label, fill="red")
            
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    def task_images_processing(self, task: Task):
        idx = 0
        for image in task.images:
            try:
                img = Image.open(image)
                results = self.__model(img, size=640)
                img_b64 = self.__save_annotated_image(img.copy(), results.pandas().xyxy[0].to_dict(orient="records"))
                task.annotated_images[f"annotated_{idx}"] = img_b64
                idx+=1
            except Exception as e:
                self.logger.error(f'while image processing: {str(e)}')
                return None
        return task