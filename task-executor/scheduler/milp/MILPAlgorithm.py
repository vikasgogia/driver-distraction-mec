from pulp import LpProblem, LpVariable, lpSum, LpBinary, LpMinimize
import numpy as np


class MILPAlgorithm():
        
    def setTasks(self, data, lambda_factor=0.5):
        self.data = data
        self.lambda_factor = lambda_factor
        self.n_tasks = len(data)
        self.tasks = range(self.n_tasks)
        
        # Initialize the problem
        self.model = LpProblem(name="task_scheduling", sense=LpMinimize)
        
        # Decision variables
        self.x = {i: LpVariable(name=f"x_{i}", cat="Binary") for i in self.tasks}
        self.s = {i: LpVariable(name=f"s_{i}", lowBound=0) for i in self.tasks}
        

    def solve(self):
        # Objective function
        total_waiting_time = lpSum((self.s[i] - self.data[i][0]) for i in self.tasks)
        dropped_ratio = lpSum((1 - self.x[i]) for i in self.tasks)
        objective = self.lambda_factor * total_waiting_time + (1 - self.lambda_factor) * dropped_ratio
        self.model += objective
        
        # Constraints
        for i in self.tasks:
            self.model += self.s[i] >= self.data[i][0]  # Start time >= arrival time
            self.model += self.s[i] + self.data[i][2] <= self.data[i][1]  # Finish time <= deadline
            if i > 0:
                self.model += self.s[i] >= self.s[i - 1] + self.data[i - 1][2]  # Order of tasks based on arrival time

        # Solve the problem
        self.model.solve()
        
        # Extract results
        optimal_order = [i for i in self.tasks if self.x[i].value() == 1]
        return optimal_order