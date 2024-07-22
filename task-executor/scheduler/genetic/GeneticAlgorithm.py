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
import random

class GeneticAlgorithm:

    def __init__(self, task_prop_total, population_size=3000, num_generations=500, mutation_rate=0.5):
        self.task_prop_total = np.array(task_prop_total)
        self.N = self.task_prop_total.shape[0] - 12
        self.task_prop = self.task_prop_total[:self.N, :]
        self.t_exp = self.task_prop[:, 1] + self.task_prop[:, 0]
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.chromosome_length = self.N
        self.tournament_size = int(0.1 * self.population_size)
        self.population = self.initialize_population()

    def initialize_population(self):
        population = np.zeros((self.population_size, self.chromosome_length), dtype=int)
        for i in range(self.population_size):
            if i == 1:
                population[i, :] = np.arange(1, self.chromosome_length + 1)
            elif i == 2:
                ind = np.argsort(self.task_prop[:, 2])
                ind1 = np.argsort(ind)
                population[i, :] = ind1
            elif i == 3:
                ind = np.argsort(self.task_prop[:, 1])
                ind1 = np.argsort(ind)
                population[i, :] = ind1
            else:
                population[i, :] = np.random.permutation(self.chromosome_length)
        return population

    def offloading_obj_fcn(self, chromosome):
        return sum(chromosome)

    def evaluate_fitness(self):
        return np.array([self.offloading_obj_fcn(ind) for ind in self.population])

    def selection(self, fitness):
        new_population = np.zeros_like(self.population)
        for i in range(self.population_size):
            tournament_indices = np.random.randint(self.population_size, size=self.tournament_size)
            best_idx = np.argmin(fitness[tournament_indices])
            new_population[i, :] = self.population[tournament_indices[best_idx], :]
        return new_population

    def mutation(self, population):
        for i in range(self.population_size):
            if random.random() < self.mutation_rate:
                population[i, :] = np.random.permutation(self.chromosome_length)
        return population

    def run(self):
        for generation in range(self.num_generations):
            fitness = self.evaluate_fitness()
            
            # Selection
            new_population = self.selection(fitness)
            
            # Mutation
            new_population = self.mutation(new_population)
            
            # Evaluate fitness of the new population
            fitness = self.evaluate_fitness()
            
            # Replace old population with new population
            self.population = new_population
            
            # Display best fitness
            best_fitness = np.min(fitness)
            print(f'Generation {generation + 1}: Best Fitness = {best_fitness}')

        # Display final result
        best_fitness = np.min(fitness)
        best_index = np.argmin(fitness)
        best_solution = self.population[best_index, :]

        t_w = np.zeros(self.N)
        sorted_indices = np.argsort(best_solution)
        for i in range(self.N):
            t_w[i] = sum(self.task_prop[sorted_indices[:best_solution[i] - 1], 2])

        t_w_n = (t_w - np.min(t_w)) / (np.max(t_w) - np.min(t_w))

        t_exp = self.task_prop[:, 1] + self.task_prop[:, 0]
        d = (t_exp <= t_w + self.task_prop[:, 2]).astype(int)

        print('Order of the tasks')
        order_index = best_solution * (1 - d)
        order_index = order_index[order_index > 0]
        print(order_index)

        print('Dropped tasks')
        dropped = best_solution * d
        dropped_index = np.where(dropped > 0)[0]
        print(dropped_index)

# Example usage
task_prop_total = [
    [0, 3.1, 1], [0, 6.1, 3], [0, 1, 3], [0, 12.1, 3], [0, 15.1, 3],
    [0, 18.1, 3], [0, 21.1, 3], [0, 3.1, 1], [0, 27.1, 3], [0, 1.1, 3],
    [0, 21.1, 3], [0, 3.1, 1], [0, 27.1, 3], [0, 1.1, 3], [0, 6.1, 3],
    [0, 1, 3], [0, 12.1, 3], [0, 15.1, 3]
]

ga = GeneticAlgorithm(task_prop_total)
ga.run()
