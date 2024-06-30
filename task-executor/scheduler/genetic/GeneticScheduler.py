import requests
import pandas as pd
import time
import threading
import os
import psutil
from queue import Queue
from executor.ImgProcessor import *
from executor.Task import *
from scheduler.genetic.GeneticAlgorithm import GeneticAlgorithm

class GeneticScheduler():
        
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.MAX_TASKS = 10
        self.pending_queue = Queue()
        self.task_queue = Queue()
        self.start_time = time.time()
        self.avg_waiting_time = 0
        self.avg_proc_time = 0
        self.avg_size_of_task = 0
        self.dropped_tasks_cnt = 0
        self.total_tasks = 0
        self.client_responses = {}
        self.runs = 0
        self.cnt = 0
        self.df = pd.DataFrame(columns=['run', 'tasks', 'avg_waiting', 'avg_processing', 'avg_size', 'drop_ratio', 'cpu_usage', 'cpu_cnt'])
    
    
    # Set up a background thread and
    # initialize image processor and ML object detection model
    def init(self):
        try:
            self.img_processor = ImgProcessor()
            self.img_processor.init_yolo_model()
            th1 = threading.Thread(target=self.process_tasks)
            th1.daemon = True
            th1.start()

        except Exception as e:
            self.logger.error(f'Error loading model: {str(e)}')
            raise e
    

    def get_queue_size(self):
        return self.task_queue.qsize() + self.pending_queue.qsize()
    
    def process_tasks(self):
        while True:
            try:
                # when task queue is empty & (pending queue is non-empty or timer has passed 2 mins)
                if self.task_queue.qsize() == 0 and (self.pending_queue.qsize() >= self.MAX_TASKS or time.time() - self.start_time > 120) :
                    ga_tasks = []
                    all_tasks = []

                    for _ in range(min(self.pending_queue.qsize(), self.MAX_TASKS + 1)):
                        pending = self.pending_queue.get()

                        all_tasks.append(pending)
                        ga_tasks.append([pending.arrival_time, pending.deadline, pending.expected_processing_time])
                    
                    if(len(ga_tasks) == 0): continue

                    geneticAlgo = GeneticAlgorithm()
                    geneticAlgo.setTasks(ga_tasks)
                    
                    [ga_tasks, min_waiting_time, min_tasks_dropped] = geneticAlgo.solve()

                    print(ga_tasks, min_tasks_dropped, min_waiting_time)
                    self.dropped_tasks_cnt += min_tasks_dropped
                    self.total_tasks += min_tasks_dropped
                    print("Dropped tasks added to Total tasks: ", self.total_tasks)

                    # empty task queue (10 elements max)
                    while not self.task_queue.empty():
                        self.task_queue.get()
                    
                    # put the best order in the task queue
                    for val in ga_tasks:
                        if(val >= len(all_tasks)): 
                            continue
                        self.task_queue.put(all_tasks[val])
                    
                    # reinitialize timer
                    self.start_time = time.time()
                    
                if self.task_queue.qsize() > 0:
                    task = self.task_queue.get()
                else:
                    continue

                task.end_wait = time.time()

                total = self.avg_waiting_time * self.total_tasks
                self.avg_waiting_time = (total + (task.end_wait - task.start_wait)) / (self.total_tasks+1)
                
                start_proc = time.time()
                task = self.img_processor.task_images_processing(task)
                end_proc = time.time()
                total = self.avg_proc_time * self.total_tasks
                self.avg_proc_time = (total + (end_proc - start_proc)) / (self.total_tasks+1)
                
                total = self.avg_size_of_task * self.total_tasks
                self.avg_size_of_task = (total + len(task.annotated_images)) / (self.total_tasks+1)
                self.total_tasks += 1
                print("Processing to Total tasks: ", self.total_tasks)
                
                requests.post(f'http://{task.id}:3000/receive-task', files=task.annotated_images)
                
            except Exception as e:
                self.logger.error(f'Error loading model: {str(e)}')
                raise e
            

    # accepts task from the task-upload api
    def submit_task(self, task: Task):
        print(self.cnt, ", ")
        self.cnt += 1
        self.pending_queue.put(task)

            
    def check_task_output(self, task_id):
        if self.client_responses[task_id].empty():
            return None
        else: 
            self.client_responses[task_id].annotated_images
            del self.client_responses[task_id]
    
    def record_run(self):
        # Getting load over 1 minute
        _, _, load15 = psutil.getloadavg()
        cpu_usage = (load15 / os.cpu_count()) * 100
        
        self.df.loc[len(self.df)] = {
            'run': self.runs,
            'tasks': self.total_tasks,
            'dropped_tasks' : self.dropped_tasks_cnt, 
            'avg_waiting': self.avg_waiting_time, 
            'avg_processing': self.avg_proc_time,
            'avg_size': self.avg_size_of_task,
            'drop_ratio': self.dropped_tasks_cnt / self.total_tasks if self.total_tasks != 0 else 0.00,
            'cpu_usage': cpu_usage,
            'cpu_cnt': os.cpu_count()
        }
        self.runs += 1
        self.avg_proc_time = 0
        self.total_tasks = 0
        self.avg_waiting_time = 0
        self.avg_size_of_task = 0
        self.dropped_tasks_cnt = 0
        self.cnt = 0