import random
import math
import pandas as pd
import numpy as np

KEY_BUDGET = 'Budget'
KEY_HARD_BUDGET = 'Hard Budget'
KEY_COST = 'Cost'
KEY_DAYS = 'Duration'
KEY_DEADLINE = 'Deadline'
KEY_TEAM_SIZE = 'Average Team Rank'
KEY_TEAM_SIZE = 'Team Size'
KEY_TEAM_RANKS = 'Team Ranks'
KEY_MET_COMMUNICATION = 'Communication'
KEY_MET_MORALE = 'Morale'
KEY_MET_SUPPORT = 'Management Support'
KEY_MET_PLANNING = 'Planning'
KEY_MET_CONFID = 'Confidence'
KEY_CODE_BUGS_TOTAL = 'Total Bugs'
KEY_CODE_BUGS_RESOLVED = 'Resolved Bugs'
KEY_CODE_COMMITS = 'Commits'
KEY_STATUS = 'Status'

STATUS_ONGOING = 1
STATUS_CANCELLED = 2
STATUS_COMPLETE = 3

eval_coefficients = {}
budget_coefficient = 5
deadline_coefficient = 5
bug_coefficient = 3

def calc_proportion_bugs_resolved(state):
    resolved = state[KEY_CODE_BUGS_TOTAL]
    total = state[KEY_CODE_BUGS_TOTAL]
    # Avoid divide by zero
    if total > 0:
        return resolved / total
    return 0

def calc_avg_team_rank(state):
    ranks = state[KEY_TEAM_RANKS]
    return np.mean(ranks) 

def populate_evaluation_coefficients():
    # TODO - add correct values here
    # eval_coefficients[KEY_CODE_BUGS_RESOLVED] = 5
    # eval_coefficients[KEY_CODE_BUGS_TOTAL] = 5
    eval_coefficients[KEY_MET_COMMUNICATION] = 5
    eval_coefficients[KEY_MET_CONFID] = 5
    eval_coefficients[KEY_MET_MORALE] = 5
    eval_coefficients[KEY_MET_PLANNING] = 5
    eval_coefficients[KEY_MET_SUPPORT] = 5


def status_to_string(status):
    if status == STATUS_CANCELLED:
        return "Cancelled"
    elif status == STATUS_COMPLETE:
        return "Complete"
    else:
        return "Ongoing"



metric_headers = [KEY_BUDGET, KEY_DEADLINE, KEY_COST, KEY_DAYS, 
                  KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, 
                  KEY_MET_COMMUNICATION, KEY_MET_CONFID, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                  KEY_TEAM_RANKS,KEY_STATUS]

class Project:
    rand = random

    def __init__(self, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        self.statesDf = pd.DataFrame(columns=metric_headers)

        (softBdgt, hardBdgt) = self.generate_budget(minBudget, maxBudget, unitBudget)
        (softDl, hardDl) = self.generate_deadline(minDeadline, maxDeadline)

        initCost = int(softBdgt * (0.5 + random.random()))
        initDuration = int(softDl * (0.5 + random.random()))

        initRow = self.make_state(STATUS_ONGOING)
        initRow[KEY_BUDGET] = softBdgt
        initRow[KEY_DEADLINE] = softDl
        initRow[KEY_COST] = initCost
        initRow[KEY_DAYS] = initDuration

        # Generate a random team (up to 6 people)
        teamRanks = []
        teamSize = random.randint(1,6)
        for i in range(0, teamSize):
            teamRanks.append(random.randint(1,6))
        initRow[KEY_TEAM_RANKS] = teamRanks

        self.append_state(initRow)
        

    def make_state(self, status):
        state = {
                    KEY_BUDGET:0, KEY_DEADLINE:0,
                    KEY_COST:0, KEY_DAYS:0, 
                    KEY_CODE_COMMITS:0, KEY_CODE_BUGS_TOTAL:0, KEY_CODE_BUGS_RESOLVED:0,
                    KEY_MET_COMMUNICATION:0, KEY_MET_CONFID:0, KEY_MET_MORALE:0, KEY_MET_PLANNING:0, KEY_MET_SUPPORT:0,
                    KEY_TEAM_RANKS:[],
                    KEY_STATUS: status
                }

        return pd.Series(state)

    def copy_row(self, row):
        return pd.Series(row, copy=True)


    def generate_budget(self, min, max, unitBudget):
        # Ideal cap on spending
        softBudget = self.rand.randint(min, max) * unitBudget
        # Absolute maximum spending permitted
        hardBudget = softBudget * (1 + math.pow(self.rand.random(), 2))
        return (softBudget, hardBudget)

    def generate_deadline(self, min, max):
        # Ideal deadline for project to be delivered by
        softDl = self.rand.randint(min, max)
        # Absolute latest project can be delivered by
        hardDl = softDl * (1 + math.pow(self.rand.random(), 2))
        return (softDl, hardDl)
        
    def get_last_state(self):
        lst = len(self.statesDf) - 1
        return self.statesDf.iloc[lst]

    def append_state(self, newState):
        self.statesDf = pd.concat([self.statesDf, newState.to_frame().T])

    # Adds a new final project state with the cancelled status
    def cancel(self):
        lastState = self.get_last_state()
        cancelState = self.make_state(STATUS_CANCELLED)
        if not lastState.empty:
            cancelState = self.copy_row(lastState)
            cancelState[KEY_STATUS] = STATUS_CANCELLED

        self.append_state(cancelState)

    def evaluate(self):
        lastState = self.get_last_state()
        return self.evaluate_state(lastState)

    def get_status(self):
        if len(self.statesDf) > 0:
            lastState = self.get_last_state()
            return lastState[KEY_STATUS]
        return None

    def __str__(self):
        s = "Project w/ " + str(len(self.statesDf)) + " states:" + "\n"
        return s + str(self.statesDf)

    def evaluate_state(self, state):
        score = 0
        numAttributes = 0

        if state[KEY_STATUS] == STATUS_CANCELLED:
            score = 0
        else:
            # TODO: find a function which handles 0s here
            cost_measure = state[KEY_BUDGET] / state[KEY_COST]
            time_measure = state[KEY_DEADLINE] / state[KEY_DAYS]

            numAttributes += 2

            score += budget_coefficient * cost_measure
            score += deadline_coefficient * time_measure
            score += bug_coefficient * calc_proportion_bugs_resolved(state)

            print("Avg team rank:", calc_avg_team_rank(state))

            for (key, coeff) in eval_coefficients.items():
                val = state[key]
                score += coeff * val
                numAttributes += 1

        print("Score:", score)
        if numAttributes > 0:
            print("Amortized Score:", score / numAttributes)

        return score




