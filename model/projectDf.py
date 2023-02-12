import random
import math
import pandas as pd
import numpy as np

KEY_ID = 'pID'
# Hard metrics
KEY_BUDGET = 'Budget'
KEY_HARD_BUDGET = 'Hard Budget'
KEY_COST = 'Cost'
KEY_DAYS = 'Duration'
KEY_DEADLINE = 'Deadline'
# Team metrics
KEY_TEAM_AVG_RANK = 'Average Team Rank'
KEY_TEAM_SIZE = 'Team Size'
KEY_TEAM_RANKS = 'Team Ranks'
# Soft metrics
KEY_MET_COMMUNICATION = 'Communication'
KEY_MET_MORALE = 'Morale'
KEY_MET_SUPPORT = 'Support'
KEY_MET_PLANNING = 'Planning'
KEY_MET_CONFID = 'Confidence'
# Code metrics
KEY_CODE_BUGS_TOTAL = 'Total Defects'
KEY_CODE_BUGS_RESOLVED = 'Fixed Defects'
KEY_CODE_COMMITS = 'Commits'
# Project metrics
KEY_STATUS = 'Status'
KEY_PROGRESS = 'Progress'

# Range of values for soft metrics 
SOFT_METRIC_MIN = 1
SOFT_METRIC_MAX = 5

STATUS_PLANNING = 'Planning'
STATUS_DEVELOPING = 'Development'
STATUS_COMPLETE = 'Complete'
STATUS_CANCELLED = 'Cancelled'

OVERRUN_SUPPORT_MULTIPLIER = 0.99
COST_PER_DEV_RANK_WEEK = 500

eval_coefficients = {}
budget_coefficient = 5
deadline_coefficient = 5
bug_coefficient = 3

# def get_headers()

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
    eval_coefficients[KEY_MET_COMMUNICATION] = 4.0
    eval_coefficients[KEY_MET_CONFID] = 3.5
    eval_coefficients[KEY_MET_MORALE] = 3
    eval_coefficients[KEY_MET_PLANNING] = 4.5
    eval_coefficients[KEY_MET_SUPPORT] = 2.1


def status_to_string(status):
    if status == STATUS_CANCELLED:
        return "Cancelled"
    elif status == STATUS_COMPLETE:
        return "Complete"
    elif status == STATUS_PLANNING:
        return "Planning"
    else:
        return "Developing"



# All Dataframe headers
metric_headers = [KEY_ID,KEY_BUDGET, KEY_DEADLINE, KEY_COST, KEY_DAYS, 
                  KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, 
                  KEY_MET_COMMUNICATION, KEY_MET_CONFID, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                  KEY_TEAM_RANKS,KEY_TEAM_AVG_RANK, 
                  KEY_STATUS,KEY_PROGRESS]

# Columns which should be used as input for the prediction model 
independent_headers = [KEY_BUDGET, KEY_DEADLINE, KEY_COST, KEY_DAYS, 
                        KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, 
                        KEY_MET_COMMUNICATION, KEY_MET_CONFID, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                        KEY_TEAM_AVG_RANK]

class Project:
    rand = random

    def __init__(self, pid, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        self.statesDf = pd.DataFrame(columns=metric_headers)

        self.projectID = pid

        # Determines complexity and scale of the project (influencing team + budget)
        # TODO: change this back to between 1-10
        projectScale = random.randint(1,4) / 10.0

        (softBdgt, hardBdgt) = self.generate_budget(minBudget, maxBudget, unitBudget, projectScale)
        (softDl, hardDl) = self.generate_deadline(minDeadline, maxDeadline, projectScale)

        initCost = int(softBdgt * (0.5 + random.random()))
        initDuration = int(softDl * (0.5 + random.random()))

        # Create an initial status for the project
        initRow = self.make_state(STATUS_PLANNING)
        initRow[KEY_BUDGET] = softBdgt
        initRow[KEY_DEADLINE] = softDl
        initRow[KEY_COST] = 0
        initRow[KEY_DAYS] = 0

        MAX_TEAM_SIZE = 6

        # Generate the development ranks for a random team
        # A larger project is permitted to have a larger dev team
        teamRanks = []
        teamSize = int(random.randint(1, MAX_TEAM_SIZE) * 10 * projectScale)
        totalRank = 0
        for i in range(0, teamSize):
            rank = random.randint(1,5)
            teamRanks.append(rank)
            totalRank += rank

        avgRank = totalRank / teamSize
        initRow[KEY_TEAM_AVG_RANK] = avgRank
        initRow[KEY_TEAM_RANKS] = teamRanks

         # Initialise soft metrics
        initRow[KEY_MET_COMMUNICATION] = round(avgRank, 2)
        initRow[KEY_MET_PLANNING] = round(1 + random.random() * 4, 2)
        initRow[KEY_MET_CONFID] = round(1 + random.random() * 4, 2)
        initRow[KEY_MET_SUPPORT] = round(1 + random.random() * 4, 2)
        initRow[KEY_MET_MORALE] = round(1 + random.random() * 4, 2)

        self.append_state(initRow)
        

    def make_state(self, status):
        state = {
                    KEY_ID:self.projectID,
                    KEY_BUDGET:0, KEY_DEADLINE:0,
                    KEY_COST:0, KEY_DAYS:0, 
                    KEY_CODE_COMMITS:0, KEY_CODE_BUGS_TOTAL:0, KEY_CODE_BUGS_RESOLVED:0,
                    KEY_MET_COMMUNICATION:0, KEY_MET_CONFID:0, KEY_MET_MORALE:0, KEY_MET_PLANNING:0, KEY_MET_SUPPORT:0,
                    KEY_TEAM_RANKS:[], KEY_TEAM_AVG_RANK:0,
                    KEY_PROGRESS: 0,
                    KEY_STATUS: status
                }

        return pd.Series(state)

    def copy_row(self, row):
        return pd.Series(row, copy=True)


    # Calculate the probability the next project state will be cancelled
    def get_cancellation_chance(self, state):
        k = 10
        support_norm = state[KEY_MET_SUPPORT] / SOFT_METRIC_MAX
        return math.exp(-k * support_norm)

    # Calculate the probability the next project state will have negative progress
    def get_neg_progress_chance(self, state):
        k = 10
        morale_norm = state[KEY_MET_MORALE] / SOFT_METRIC_MAX
        return 0.2*math.exp(-k * morale_norm)



    def generate_budget(self, min, max, unitBudget, projScale):
        # Ideal cap on spending
        softBudget = self.rand.randint(min, max) * unitBudget
        # Absolute maximum spending permitted
        hardBudget = softBudget * (1 + math.pow(self.rand.random(), 2))
        return (softBudget, hardBudget)


    def generate_deadline(self, min, max, projScale):
        # Ideal deadline for project to be delivered by
        softDl = self.rand.randint(min, max)
        # Absolute latest project can be delivered by
        hardDl = softDl * (1 + math.pow(self.rand.random(), 2))
        return (softDl, hardDl)

        
    def get_last_state(self):
        lst = len(self.statesDf) - 1
        return self.statesDf.iloc[lst]


    def append_state(self, newState):
        self.statesDf = pd.concat([self.statesDf, newState.to_frame().T], ignore_index=True)


    def add_commits_and_bugs(self, newState):
        # Get the number of unresolved bugs in the codebase
        existingBugs = newState[KEY_CODE_BUGS_TOTAL] - newState[KEY_CODE_BUGS_RESOLVED]

        devTeam = newState[KEY_TEAM_RANKS]
        devTeamSize = len(devTeam)

        # Number of commits is proportional to the morale and dev team size
        newCommits = random.randint(1, int(newState[KEY_MET_MORALE]) * devTeamSize)
        newBugs = 0
        newResolvedBugs = 0

        existingBugs = newState[KEY_CODE_BUGS_TOTAL] - newState[KEY_CODE_BUGS_RESOLVED]

        for rank in devTeam:
            # Calculate the chance of a developer not fixing a bug, based on their experience
            # e.g.
            #   Rank=0 means 75% chance of creating a bug; 
            #   Rank=5 means 30% chance of creating a bug
            bugLikelihood = 0.75 * math.exp(rank / 5)

            # TODO: include some coefficients so these can be varied based on team size and metrics
            # Include some random number of bugs
            commitBugs = 0
            for i in range(0, random.randint(0,20)):
                if random.random() < bugLikelihood:
                    commitBugs = random.randint(0,3)
                    
            newBugs += commitBugs
            # Fix some number of bugs
            commitResolvedBugs = random.randint(0, commitBugs)
            # Bugs which already exist in the code may be solved
            if existingBugs > 0:
                existingResolvedBugs = random.randint(0, existingBugs)
                existingBugs -= existingResolvedBugs
                newResolvedBugs += existingResolvedBugs

            newResolvedBugs += commitResolvedBugs

        newState[KEY_CODE_COMMITS] += newCommits
        newState[KEY_CODE_BUGS_TOTAL] += newBugs
        newState[KEY_CODE_BUGS_RESOLVED] += newResolvedBugs


    # Set the new progress of the project, based on the team's soft metrics
    def update_progress(self, state):
        comm = state[KEY_MET_COMMUNICATION]
        planning = state[KEY_MET_PLANNING]
        morale = state[KEY_MET_MORALE]
        teamsize = int(math.log(len(state[KEY_TEAM_RANKS])+1))

        delta = (comm + planning + morale) * teamsize / 500

        if state[KEY_PROGRESS] > 0:
            if random.random() < self.get_neg_progress_chance(state):
                # Proportion of progress which is reversed (Square-Law to reduce effect)
                negProgress = pow(random.random(),2)
                delta = -negProgress * state[KEY_PROGRESS]
        
        state[KEY_PROGRESS] = min(1, state[KEY_PROGRESS] + delta)


    def simulate(self):
        dl = self.get_last_state()[KEY_DEADLINE]

        # Store newly-generated states in a list, so they can be added to the dataframe together
        newStates = []
        prevState = self.get_last_state()

        weeksPlanning = int(prevState[KEY_MET_PLANNING])
        weekCost = 0

        stopSim = False

        # Simulate a given number of weeks of project development
        # for week in range(0, weeksToSim):
        while not stopSim:
            newState = self.copy_row(prevState)

            # If Planning Stage is complete
            if newState[KEY_STATUS] == STATUS_PLANNING:
                weekCost += random.randint(100,2000)
                if newState[KEY_DAYS] >= weeksPlanning * 7:
                    newState[KEY_STATUS] = STATUS_DEVELOPING
            # If in development and the dev team contains at least one person
            elif newState[KEY_STATUS] == STATUS_DEVELOPING and len(newState[KEY_TEAM_RANKS]) > 0:
                self.add_commits_and_bugs(newState)

                # Calculate cost of paying development team for the week
                for dev in newState[KEY_TEAM_RANKS]:
                    weekCost += dev * COST_PER_DEV_RANK_WEEK

                self.update_progress(newState)

                if newState[KEY_PROGRESS] >= 1:
                    newState[KEY_STATUS] = STATUS_COMPLETE
                    stopSim = True

            cancellation_chance = self.get_cancellation_chance(newState)

            if random.random() < cancellation_chance:
                newState[KEY_STATUS] = STATUS_CANCELLED
                stopSim = True

            # Every week the project overruns, the support of executives decreases
            if newState[KEY_DAYS] > dl or newState[KEY_COST] > newState[KEY_BUDGET]:
                newState[KEY_MET_SUPPORT] *= OVERRUN_SUPPORT_MULTIPLIER

            newState[KEY_COST] += weekCost
            newState[KEY_DAYS] += 7
            prevState = newState
            newStates.append(newState)

        # Add the new states to the existing data
        self.statesDf = pd.concat([self.statesDf, pd.DataFrame(newStates)], ignore_index=True)

    # Adds a new final project state with the cancelled status
    def cancel(self):
        lastState = self.get_last_state()
        cancelState = self.make_state(STATUS_CANCELLED)
        if not lastState.empty:
            cancelState = self.copy_row(lastState)
            cancelState[KEY_STATUS] = STATUS_CANCELLED

        self.append_state(cancelState)

    # Adds a new final project state with the cancelled status
    def complete(self):
        lastState = self.get_last_state()
        completeState = self.make_state(STATUS_COMPLETE)
        if not lastState.empty:
            completeState = self.copy_row(lastState)
            completeState[KEY_STATUS] = STATUS_COMPLETE

        self.append_state(completeState)

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


    # Logistic function to compress range of values into [0,2]
    # x is a float between 0 and 2
    def sigmoid_func(self, x):
        k = 5       # Steepness
        x_0 = 1     # Centered around 1
        exp = math.exp(-k*(x-x_0))
        return 1 / (1+exp)

    def tanh_func(self, x):
        k = 3       # Gradient steepness
        x_0 = 3     # Centered around 1
        c = 1       # Shift up above y-axis
        m = 0.5     # Overall scaling
        return m * (math.tanh(k*x - x_0) + c)


    # Divides num by denom, then standardises with a logistic function
    # Avoids dividing by zero
    def calc_ratio_safe(self, num, denom):
        a = max(1.0, num)
        b = max(1.0, denom)
        return self.sigmoid_func(a/b) 


    def evaluate_state(self, state):
        score = 0
        numAttributes = 0

        if state[KEY_STATUS] == STATUS_CANCELLED:
            score = 0
        else:
            cost_measure = self.calc_ratio_safe(state[KEY_BUDGET], state[KEY_COST])
            time_measure = self.calc_ratio_safe(state[KEY_DEADLINE], state[KEY_DAYS])

            numAttributes += 2

            score += budget_coefficient * cost_measure
            score += deadline_coefficient * time_measure
            score += bug_coefficient * calc_proportion_bugs_resolved(state)

            # print("Avg team rank:", calc_avg_team_rank(state))

            # for (key, coeff) in eval_coefficients.items():
            #     val = state[key]
            #     score += coeff * val
            #     numAttributes += 1

        # print("Score:", score)
        amortisedScore = 0
        if numAttributes > 0:
            amortisedScore = score / numAttributes
            # print("Amortized Score:", amortisedScore)

        return amortisedScore

    def get_dataframe(self):
        return self.statesDf

    def get_labelled_samples(self, k):
        # We can only take as many samples as there are states
        k = min(k, len(self.statesDf))
        sampleDf = self.statesDf.sample(k)

        successScore = self.evaluate()
        success = 0
        
        if successScore > 4:
            success = 1
        elif self.get_last_state()[KEY_STATUS] == STATUS_CANCELLED:
            success = -1
        
        sampleDf.insert(len(sampleDf.columns),'Success',success)
        # Remove the team ranks
        return sampleDf.drop(columns=[KEY_TEAM_RANKS],axis=1)



