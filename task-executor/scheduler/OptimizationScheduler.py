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
from scheduler.milp.MILPAlgorithm import MILPAlgorithm

class OptimizationScheduler:
        
    def __init__(self, algorithm=GeneticAlgorithm()):
        self.algorithm = algorithm
        self.logger = logging.getLogger(__name__)
        self.__MAX_TASKS = 10
        self.__pending_queue = Queue()
        self.__task_queue = Queue()
        self.__start_time = time.time()

        self.total_tasks = 0
        self.__client_responses = {}
        self.avg_waiting_time = 0
        self.avg_proc_time = 0
        self.avg_size_of_task = 0
        self.dropped_tasks_cnt = 0
        self.__runs = 0
        self.df = pd.DataFrame(columns=['run', 'tasks', 'avg_waiting', 'avg_processing', 'avg_size', 'drop_ratio', 'cpu_usage', 'cpu_cnt'])
            
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
    
    def get_queue_size(self):
        return self.__get_queue_size() + self.__pending_queue.qsize()
    
    def __get_queue_size(self):
        return self.__task_queue.qsize()
    
    def __process_tasks(self):
        while True:
            try:
                if self.__get_queue_size() == 0 and (self.__pending_queue.qsize() >= self.__MAX_TASKS or time.time() - self.__start_time > 120) :
                    ga_tasks = []
                    all_tasks = []
                    for _ in range(min(self.__pending_queue.qsize(), self.__MAX_TASKS + 1)):
                        pending = self.__pending_queue.get()
                        # self.__task_queue.put(pending)
                        all_tasks.append(pending)
                        ga_tasks.append([pending.arrival_time, pending.deadline, pending.expected_processing_time])
                    
                    print(ga_tasks)

                    self.algorithm.setTasks(ga_tasks)
                    [ga_tasks, min_waiting_time, min_tasks_dropped] = self.algorithm.solve()

                    print(ga_tasks, min_tasks_dropped, min_waiting_time)
                    self.dropped_tasks_cnt += min_tasks_dropped

                    # empty task queue (10 elements max)
                    while not self.__task_queue.empty():
                        self.__task_queue.get()
                    
                    # put the best order in the task queue
                    for val in ga_tasks:
                        if(val >= len(all_tasks)): 
                            continue
                        self.__task_queue.put(all_tasks[val])
                    
                    # reinitialize timer
                    self.__start_time = time.time()
                    
                if self.__get_queue_size() > 0:
                    task = self.__task_queue.get()
                else:
                    continue
                task.end_wait = time.time()
                
                # 3 minutes waiting time is a deadline
                if (task.end_wait - task.start_wait) > 180:
                    self.total_tasks += 1
                    self.dropped_tasks_cnt += 1
                    continue

                total = self.avg_waiting_time * self.total_tasks
                self.avg_waiting_time = (total + (task.end_wait - task.start_wait)) / (self.total_tasks+1)
                
                start_proc = time.time()
                task = self.__img_processor.task_images_processing(task)
                end_proc = time.time()
                total = self.avg_proc_time * self.total_tasks
                self.avg_proc_time = (total + (end_proc - start_proc)) / (self.total_tasks+1)
                
                total = self.avg_size_of_task * self.total_tasks
                self.avg_size_of_task = (total + len(task.annotated_images)) / (self.total_tasks+1)
                self.total_tasks += 1
                
                requests.post(f'http://{task.id}:3000/receive-task', files=task.annotated_images)
                
            except Exception as e:
                self.logger.error(f'Error loading model: {str(e)}')
                raise e
            
    def submit_task(self, task: Task):
        self.__pending_queue.put(task)
            
    def check_task_output(self, task_id):
        if self.__client_responses[task_id].empty():
            return None
        else: 
            self.__client_responses[task_id].annotated_images
            del self.__client_responses[task_id]
    
    def record_run(self):
        # Getting load over 1 minute
        _, _, load15 = psutil.getloadavg()
        cpu_usage = (load15 / os.cpu_count()) * 100
        
        self.df.loc[len(self.df)] = {
            'run': self.__runs, 
            'tasks': self.total_tasks, 
            'avg_waiting': self.avg_waiting_time, 
            'avg_processing': self.avg_proc_time,
            'avg_size': self.avg_size_of_task,
            'drop_ratio': self.dropped_tasks_cnt / self.total_tasks if self.total_tasks != 0 else 0.00,
            'cpu_usage': cpu_usage,
            'cpu_cnt': os.cpu_count()
        }
        self.__runs += 1