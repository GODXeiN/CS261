import random
import math

class Project:
    rand = random

    def __init__(self):
        return None
        
    def make(self, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        self.gen_budget(minBudget, maxBudget, unitBudget)
        self.gen_deadline(minDeadline, maxDeadline)
        self.gen_team()
        self.gen_result()
        self.calc_success()

    def __str__(self):
        vals = self.as_array()
        row = str(vals[0])
        for i in range(1, len(vals)):
            row += "," + str(vals[i])
        return row

    def get_features(self, features):
        vals = []
        for f in features:
            if f == 'Budget':
                vals.append(self.budget)
            elif f == 'Budget Tolerance':
                vals.append(self.budget_tolerance)
            elif f == 'Communication':
                vals.append(self.communication)
            elif f == 'Average Team Experience':
                vals.append(self.avg_team_yrs)
            elif f == 'Team Size':
                vals.append(self.team_size)
            elif f == 'Deadline':
                vals.append(self.deadline)
            elif f == 'Cost':
                vals.append(self.cost)
            elif f == 'Days Taken':
                vals.append(self.days_taken)
        return vals

    def get_headers(self):
        return ['Budget', 'Budget Tolerance', 'Communication',
                'Average Team Experience', 'Team Size', 'Deadline', 
                'Cost', 'Days Taken',
                'Budget Success', 'Deadline Success', 'Team Success',
                'Success']

    def as_array(self):
        return [self.budget, self.budget_tolerance, self.communication, 
                self.avg_team_yrs, self.team_size, self.deadline, 
                self.cost, self.days_taken, 
                self.budget_success, self.deadline_success, self.team_success,
                self.success]
        
    def gen_budget(self, min, max, unit):
        self.budget = self.rand.randint(min, max) * unit
        # Represents how much the project is allowed to go overbudget
        self.budget_tolerance = round(1 + self.rand.random() / 2, 2)
        
    def gen_deadline(self, min, max): 
        self.deadline = self.rand.randint(min, max)

    def gen_team(self):
        self.communication = self.rand.randint(0,4)
        self.team_size = self.rand.randint(2,20)
        # Average years of experience of each team member
        self.avg_team_yrs = round(1 + self.rand.random() * 15, 2)

    def gen_result(self):
        self.days_taken = int(self.deadline * (self.rand.random() + 0.5))
        self.team_member_cost = (self.avg_team_yrs + 2) * 10000 * self.days_taken / 200
        self.cost = int(self.team_size * self.team_member_cost * (1 + self.rand.random() / 4))
    
    def calc_success(self):
        # Check if project was under budget
        if self.cost <= self.budget * self.budget_tolerance:
            self.budget_success = 1
        else:
            self.budget_success = 0

        # Check if project completed in the given deadline
        if self.days_taken <= self.deadline:
            self.deadline_success = 1
        else:
            self.deadline_success = 0


        comb_team_metric = self.avg_team_yrs * (self.communication + 1) / 100

        # Logistic Function for the chance of the team succeeding
        #   see "Sigmoid Function"
        x_0 = 0.5   # Center-point
        k = 4       # Steepness of slope
        chance_success = 1 / (1 + pow(math.e, -k * (comb_team_metric - x_0)))

        if chance_success >= 0.5:
            self.team_success = 1
        else:
            self.team_success = 0

        # Determine how much over-budget/over-time the project is
        overbudget_deg = min(2, self.budget / self.cost)
        overtime_deg = min(2, self.deadline / self.days_taken)
        # Average to get a float in range 0-1
        self.overall_success = round((overbudget_deg + overtime_deg) / 4, 2)

        # 50% random chance to fail
        if self.team_success == 0 and random.random() < 0.5:
            self.success = '0'
        # If both budget and deadline fail, then project fails
        elif self.budget_success * self.deadline_success == 0:
            self.success = '0'
        else:
            self.success = '1'

        return self.success