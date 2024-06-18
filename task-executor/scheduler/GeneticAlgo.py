from geneticalgorithm import geneticalgorithm as ga
import numpy as np

# Problem parameters
N = 10  # Number of tasks
lambda_factor = 0.5

# Sample data for each task (arrival time, deadline, processing time)
data = np.array([
    [1, 10, 2],  # Task 1
    [2, 12, 3],  # Task 2
    [1, 9, 2],   # Task 3
    [3, 13, 3],  # Task 4
    [4, 14, 1],  # Task 5
    [2, 11, 2],  # Task 6
    [5, 16, 4],  # Task 7
    [6, 17, 3],  # Task 8
    [4, 15, 2],  # Task 9
    [7, 18, 3]   # Task 10
])

# Initialize CPU availability time
cpu_time = 0

# Initialize global variables for tracking minimums
min_total_waiting_time = float('inf')
min_total_dropped_tasks = float('inf')
best_solution = None

def f(X):
    global cpu_time, min_total_waiting_time, min_total_dropped_tasks, best_solution
    cpu_time = 0
    total_waiting_time = 0
    total_dropped = 0

    for i in range(N):
        if X[i] == 1:  # Task i is scheduled
            arrival = data[i][0]
            deadline = data[i][1]
            processing = data[i][2]
            start_time = max(cpu_time, arrival)
            finish_time = start_time + processing

            # Start processing time constraint check
            if not (arrival <= start_time <= deadline - processing):
                return float('inf')  # Penalize violation of start processing time constraint

            # Calculate actual waiting time
            waiting_time = start_time - arrival

            # Check waiting time constraint
            if not (0 <= waiting_time <= deadline - arrival - processing):
                return float('inf')  # Penalize violation of waiting time constraint

            # Update CPU time
            cpu_time = finish_time

            # Calculate normalized waiting time for the objective
            normalized_waiting_time = waiting_time / (deadline - arrival - processing)
            total_waiting_time += normalized_waiting_time
        else:
            total_dropped += 1  # Count this task as dropped if not scheduled

    # Update global minimums if current solution is better
    if total_waiting_time < min_total_waiting_time:
        min_total_waiting_time = total_waiting_time
        min_total_dropped_tasks = total_dropped
        best_solution = X.copy()

    dropped_ratio = total_dropped / N  # Calculate the ratio of dropped tasks
    objective = lambda_factor * total_waiting_time + (1 - lambda_factor) * dropped_ratio
    print(f"Evaluation: Total Waiting Time = {total_waiting_time}, Total Dropped = {total_dropped}, Dropped Ratio = {dropped_ratio}, Objective = {objective}")
    return objective

varbound = np.array([[0, 1]] * N)

algorithm_param = {
    'max_num_iteration': 50,
    'population_size': 100,
    'mutation_probability': 0.1,
    'elit_ratio': 0.01,
    'crossover_probability': 0.5,
    'parents_portion': 0.3,
    'crossover_type': 'uniform',
    'max_iteration_without_improv': None
}

model = ga(
    function=f,
    dimension=N,
    variable_type='bool',
    variable_boundaries=varbound,
    algorithm_parameters=algorithm_param
)

model.run()

# Print the minimum values after GA execution
print("Minimum Total Normalized Waiting Time:", min_total_waiting_time)
print("Minimum Total Dropped Tasks:", min_total_dropped_tasks)

# Decode the best solution to get the order of tasks
if best_solution is not None:
    task_order = [i for i in range(N) if best_solution[i] == 1]
    print("Best order of tasks to run:", task_order)
else:
    print("No feasible solution found.")
