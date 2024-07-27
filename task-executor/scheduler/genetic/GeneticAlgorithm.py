# from geneticalgorithm import geneticalgorithm as ga
# import numpy as np

# class GeneticAlgorithm():

#     def setTasks(self, tasks, lambda_factor=0.5, max_iterations=100, population_size=100):
#         self.tasks = tasks
#         self.N = len(tasks)  # Number of tasks
#         self.lambda_factor = lambda_factor
#         self.max_iterations = max_iterations
#         self.population_size = population_size
#         self.cpu_time = 0
#         self.min_total_waiting_time = float('inf')
#         self.min_total_dropped_tasks = float('inf')
#         self.best_solution = None
#         self.best_objective = float('inf')


#     def objective_function(self, X):
#         self.cpu_time = 0
#         total_waiting_time = 0
#         total_dropped = 0

#         for i in range(self.N):
#             if X[i] == 1:  # Task i is scheduled
#                 arrival = self.tasks[i][0]
#                 deadline = self.tasks[i][1]
#                 processing = self.tasks[i][2]
#                 start_time = max(self.cpu_time, arrival)
#                 finish_time = start_time + processing

#                 # Start processing time constraint check
#                 if not (arrival <= start_time <= deadline - processing):
#                     print("start processign time check inf: ", start_time, arrival, deadline, processing)
#                     return float('inf')  # Penalize violation of start processing time constraint

#                 # Calculate actual waiting time
#                 waiting_time = start_time - arrival

#                 # Check waiting time constraint
#                 if not (0 <= waiting_time <= deadline - arrival - processing):
#                     print("start waiting time check inf: ", start_time, arrival, deadline, processing)
#                     return float('inf')  # Penalize violation of waiting time constraint

#                 # Update CPU time
#                 self.cpu_time = finish_time

#                 # Calculate normalized waiting time for the objective
#                 normalized_waiting_time = waiting_time / (deadline - arrival - processing)
#                 total_waiting_time += normalized_waiting_time
#             else:
#                 total_dropped += 1  # Count this task as dropped if not scheduled

#         # Update global minimums if current solution is better
                    
#         # if total_waiting_time < self.min_total_waiting_time:
#         # if total_dropped < self.min_total_dropped_tasks and total_waiting_time < self.min_total_waiting_time:
#         #     self.min_total_waiting_time = total_waiting_time
#         #     self.min_total_dropped_tasks = total_dropped
#         #     self.best_solution = X.copy()

#         dropped_ratio = total_dropped / self.N  # Calculate the ratio of dropped tasks
#         objective = self.lambda_factor * total_waiting_time + (1 - self.lambda_factor) * dropped_ratio
        
#         if objective < self.best_objective:
#             self.best_objective = objective
#             self.best_solution = X.copy()
#             self.min_total_waiting_time = total_waiting_time
#             self.min_total_dropped_tasks = total_dropped

#         return objective

#     def solve(self):
#         if(self.N <= 0): return
#         varbound = np.array([[0, 1]] * self.N)

#         algorithm_param = {
#             'max_num_iteration': self.max_iterations,
#             'population_size': self.population_size,
#             'mutation_probability': 0.1,
#             'elit_ratio': 0.01,
#             'crossover_probability': 0.5,
#             'parents_portion': 0.3,
#             'crossover_type': 'uniform',
#             'max_iteration_without_improv': None
#         }

#         model = ga(
#             function=self.objective_function,
#             dimension=self.N,
#             variable_type='bool',
#             variable_boundaries=varbound,
#             algorithm_parameters=algorithm_param
#         )

#         model.run()

#         # Decode the best solution to get the order of tasks
#         if self.best_solution is not None:
#             task_order = [i for i in range(self.N) if self.best_solution[i] == 1]
#             return task_order, self.min_total_waiting_time, self.min_total_dropped_tasks
#         else:
#             return None, self.min_total_waiting_time, self.min_total_dropped_tasks

import numpy as np

class GeneticAlgorithm:
    
    def __init__(self, task_prop_total, t_current=0, population_size=3000, num_generations=100, mutation_rate=0.7):
        self.task_prop_total = np.array(task_prop_total)
        print("submitted tasks = ", task_prop_total)
        self.t_current = t_current
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.chromosome_length = self.task_prop_total.shape[0]
        self.tournament_size = int(0.1 * population_size)

    def offloading_obj_fcn2(self, x):
        N = self.task_prop.shape[0]
        t_w = np.zeros(N)

        x_sort, ind = np.sort(x), np.argsort(x)

        for i in range(N):
            for j in range(x[i] - 1):
                t_w[i] += self.task_prop[ind[j], 2]

        t_w_n = (t_w - np.min(t_w)) / (np.max(t_w) - np.min(t_w))
        t_exp = self.task_prop[:, 1] + self.task_prop[:, 0]
        d = 1 * (t_exp - self.t_current <= t_w + self.task_prop[:, 2])
        W_ave_total = np.sum(t_w_n * d) / N
        D = np.sum(d) / N

        lambda_ = 0.5
        y = lambda_ * W_ave_total + (1 - lambda_) * D

        return y

    def initialize_population(self):
        self.population = np.zeros((self.population_size, self.chromosome_length), dtype=int)
        for i in range(self.population_size):
            if i == 0:
                self.population[i, :] = np.argsort(self.task_prop[:, 0])  # First come first served
            elif i == 2:
                self.population[i, :] = np.argsort(self.task_prop[:, 2])  # Shortest task first
            elif i == 3:
                self.population[i, :] = np.argsort(self.task_prop[:, 1])  # Shortest deadline first
            else:
                self.population[i, :] = np.random.permutation(self.chromosome_length)

    def run_ga(self):
        self.task_prop = self.task_prop_total[:self.chromosome_length, :]
        self.initialize_population()

        for generation in range(self.num_generations):
            fitness = np.zeros(self.population_size)
            for ii in range(self.population_size):
                fitness[ii] = self.offloading_obj_fcn2(self.population[ii, :])

            new_population = np.zeros_like(self.population)
            for i in range(self.population_size):
                tournament_indices = np.random.randint(0, self.population_size, self.tournament_size)
                best_idx = tournament_indices[np.argmin(fitness[tournament_indices])]
                new_population[i, :] = self.population[best_idx, :]

            for i in range(self.population_size):
                if np.random.rand() < self.mutation_rate:
                    new_population[i, :] = np.random.permutation(self.chromosome_length)

            for ii in range(self.population_size):
                fitness[ii] = self.offloading_obj_fcn2(new_population[ii, :])

            self.population = new_population

            best_fitness = np.min(fitness)
            print(f'Generation {generation}: Best Fitness = {best_fitness}')

        self.best_fitness = np.min(fitness)
        self.best_index = np.argmin(fitness)
        self.best_solution = self.population[self.best_index, :]

    def get_best_order(self):
        t_w = np.zeros(self.chromosome_length)
        ind = np.argsort(self.best_solution)
        for i in range(self.chromosome_length):
            for j in range(self.best_solution[i] - 1):
                t_w[i] += self.task_prop[ind[j], 2]

        t_w_n = (t_w - np.min(t_w)) / (np.max(t_w) - np.min(t_w))
        t_exp = self.task_prop[:, 1] + self.task_prop[:, 0]
        d = 1 * (t_exp - self.t_current <= t_w + self.task_prop[:, 2])

        best_solution_sort = np.sort(self.best_solution)
        ind_best = np.argsort(self.best_solution)
        ind_best_served = []
        ind_best_dropped = []

        for i in range(self.chromosome_length):
            if d[ind_best[i]] == 0:
                ind_best_served.append(ind_best[i])
            else:
                ind_best_dropped.append(ind_best[i])

        return ind_best_served, ind_best_dropped


# Example usage:
# task_prop_total = np.array([
#     [0, 3.1, 1],
#     [0, 6.1, 3],
#     [0, 1, 3],
#     [0, 12.1, 2],
#     [0, 15.1, 3],
#     [0, 18.1, 3],
#     [0, 21.1, 3],
#     [0, 3.1, 1],
#     [0, 27.1, 3],
#     [0, 1.1, 3],
#     [0, 21.1, 3],
#     [0, 3.1, 1],
#     [0, 27.1, 3],
#     [0, 1.1, 3],
#     [0, 6.1, 1],
#     [0, 1, 3],
#     [0, 12.1, 3],
#     [0, 15.1, 3]
# ])

# scheduler = GeneticAlgorithm(task_prop_total)
# scheduler.run_ga()
# best_order, dropped_tasks = scheduler.get_best_order()

# print('Order of the tasks:', best_order)
# print('Dropped task index:', dropped_tasks)
