import threading
from enum import Enum
from queue import Queue
from executor.ImgProcessor import *
from executor.Task import *

class Scheduler():
    
    class Scheduling(Enum):
        FCFS = 1
        SJF = 2
        
    def __init__(self, algorithm=Scheduling.FCFS):
        self.logger = logging.getLogger(__name__)
        self.__algorithm = algorithm
        self.__task_queue = Queue()
        self.__client_responses = {}
            
    def init(self):
        try:
            self.__img_processor = ImgProcessor()
            self.__img_processor.init_yolo_model()
            
            th1 = threading.Thread(target=self.__process_tasks)
            th1.daemon = True
            th1.start()
        except Exception as e:
            self.logger.error(f'Error loading model: {str(e)}')
            raise e
            
    def __process_tasks(self):
        while True:
            try:
                task = self.__task.get()
                task = self.__img_processor.task_images_processing(task)
                self.client_responses[task.id] = task
            except Exception as e:
                self.logger.error(f'Error loading model: {str(e)}')
                raise e
            
    def submit_task(self, task: Task):
        if self.__algorithm == self.Scheduling.FCFS:
            self.__task_queue.put(task)
            
    def check_task_output(self, task_id):
        if self.__client_responses[task_id].empty():
            return None
        else: 
            self.__client_responses[task_id].annotated_images
            del self.__client_responses[task_id]
        