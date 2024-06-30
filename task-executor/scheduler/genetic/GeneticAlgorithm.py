from geneticalgorithm import geneticalgorithm as ga
import numpy as np

class GeneticAlgorithm():

    def setTasks(self, tasks, lambda_factor=0.5, max_iterations=100, population_size=100):
        self.tasks = tasks
        self.N = len(tasks)  # Number of tasks
        self.lambda_factor = lambda_factor
        self.max_iterations = max_iterations
        self.population_size = population_size
        self.cpu_time = 0
        self.min_total_waiting_time = float('inf')
        self.min_total_dropped_tasks = float('inf')
        self.best_solution = None
        self.best_objective = float('inf')


    def objective_function(self, X):
        self.cpu_time = 0
        total_waiting_time = 0
        total_dropped = 0

        for i in range(self.N):
            if X[i] == 1:  # Task i is scheduled
                arrival = self.tasks[i][0]
                deadline = self.tasks[i][1]
                processing = self.tasks[i][2]
                start_time = max(self.cpu_time, arrival)
                finish_time = start_time + processing

                # Start processing time constraint check
                if not (arrival <= start_time <= deadline - processing):
                    print("start processign time check inf: ", start_time, arrival, deadline, processing)
                    return float('inf')  # Penalize violation of start processing time constraint

                # Calculate actual waiting time
                waiting_time = start_time - arrival

                # Check waiting time constraint
                if not (0 <= waiting_time <= deadline - arrival - processing):
                    print("start waiting time check inf: ", start_time, arrival, deadline, processing)
                    return float('inf')  # Penalize violation of waiting time constraint

                # Update CPU time
                self.cpu_time = finish_time

                # Calculate normalized waiting time for the objective
                normalized_waiting_time = waiting_time / (deadline - arrival - processing)
                total_waiting_time += normalized_waiting_time
            else:
                total_dropped += 1  # Count this task as dropped if not scheduled

        # Update global minimums if current solution is better
                    
        # if total_waiting_time < self.min_total_waiting_time:
        # if total_dropped < self.min_total_dropped_tasks and total_waiting_time < self.min_total_waiting_time:
        #     self.min_total_waiting_time = total_waiting_time
        #     self.min_total_dropped_tasks = total_dropped
        #     self.best_solution = X.copy()

        dropped_ratio = total_dropped / self.N  # Calculate the ratio of dropped tasks
        objective = self.lambda_factor * total_waiting_time + (1 - self.lambda_factor) * dropped_ratio
        
        if objective < self.best_objective:
            self.best_objective = objective
            self.best_solution = X.copy()
            self.min_total_waiting_time = total_waiting_time
            self.min_total_dropped_tasks = total_dropped

        return objective

    def solve(self):
        if(self.N <= 0): return
        varbound = np.array([[0, 1]] * self.N)

        algorithm_param = {
            'max_num_iteration': self.max_iterations,
            'population_size': self.population_size,
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'crossover_probability': 0.5,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': None
        }

        model = ga(
            function=self.objective_function,
            dimension=self.N,
            variable_type='bool',
            variable_boundaries=varbound,
            algorithm_parameters=algorithm_param
        )

        model.run()

        # Decode the best solution to get the order of tasks
        if self.best_solution is not None:
            task_order = [i for i in range(self.N) if self.best_solution[i] == 1]
            return task_order, self.min_total_waiting_time, self.min_total_dropped_tasks
        else:
            return None, self.min_total_waiting_time, self.min_total_dropped_tasks
