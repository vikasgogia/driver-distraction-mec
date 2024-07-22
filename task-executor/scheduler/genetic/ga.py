import numpy as np
import random

# Define global variables
task_prop_total = np.array([[0, 3.1, 1],
                            [0, 6.1, 3],
                            [0, 1, 3],
                            [0, 12.1, 3],
                            [0, 15.1, 3],
                            [0, 18.1, 3],
                            [0, 21.1, 3],
                            [0, 3.1, 1],
                            [0, 27.1, 3],
                            [0, 1.1, 3],
                            [0, 21.1, 3],
                            [0, 3.1, 1],
                            [0, 27.1, 3],
                            [0, 1.1, 3],
                            [0, 6.1, 3],
                            [0, 1, 3],
                            [0, 12.1, 3],
                            [0, 15.1, 3]])

N = task_prop_total.shape[0] - 12
task_prop = task_prop_total[:N, :]
t_exp = task_prop[:, 1] + task_prop[:, 0]

# GA parameters
populationSize = 3000
numberOfGenerations = 500
mutationRate = 0.5
chromosomeLength = N
tournamentSize = int(0.1 * populationSize)

# Define the objective function
def offloading_obj_fcn(chromosome):
    # Placeholder for actual objective function implementation
    # For demonstration, returning sum of chromosome values
    return sum(chromosome)

# Initialize population
population = np.zeros((populationSize, chromosomeLength), dtype=int)
for i in range(populationSize):
    if i == 1:
        population[i, :] = np.arange(1, chromosomeLength + 1)
    elif i == 2:
        ind = np.argsort(task_prop[:, 2])
        ind1 = np.argsort(ind)
        population[i, :] = ind1
    elif i == 3:
        ind = np.argsort(task_prop[:, 1])
        ind1 = np.argsort(ind)
        population[i, :] = ind1
    else:
        population[i, :] = np.random.permutation(chromosomeLength)

# Main GA loop
for generation in range(numberOfGenerations):
    fitness = np.array([offloading_obj_fcn(ind) for ind in population])
    
    # Selection (tournament selection)
    newPopulation = np.zeros_like(population)
    for i in range(populationSize):
        tournamentIndices = np.random.randint(populationSize, size=tournamentSize)
        bestIdx = np.argmin(fitness[tournamentIndices])
        newPopulation[i, :] = population[tournamentIndices[bestIdx], :]
    
    # Mutation
    for i in range(populationSize):
        if random.random() < mutationRate:
            newPopulation[i, :] = np.random.permutation(chromosomeLength)
    
    # Evaluate fitness of the new population
    fitness = np.array([offloading_obj_fcn(ind) for ind in newPopulation])
    
    # Replace old population with new population
    population = newPopulation
    
    # Display best fitness
    bestFitness = np.min(fitness)
    print(f'Generation {generation + 1}: Best Fitness = {bestFitness}')

# Display final result
bestFitness = np.min(fitness)
bestIndex = np.argmin(fitness)
bestSolution = population[bestIndex, :]

t_w = np.zeros(N)
sorted_indices = np.argsort(bestSolution)
for i in range(N):
    t_w[i] = sum(task_prop[sorted_indices[:bestSolution[i] - 1], 2])

t_w_n = (t_w - np.min(t_w)) / (np.max(t_w) - np.min(t_w))

t_exp = task_prop[:, 1] + task_prop[:, 0]
d = (t_exp <= t_w + task_prop[:, 2]).astype(int)

print('Order of the tasks')
order_index = bestSolution * (1 - d)
order_index = order_index[order_index > 0]
print(order_index)

print('Dropped tasks')
dropped = bestSolution * d
dropped_index = np.where(dropped > 0)[0]
print(dropped_index)
