import random
import math
import pandas as pd
import numpy as np

# TODO: make list of usages for each metric


KEY_ID = 'pID'
# Hard metrics
KEY_BUDGET = 'Budget'
KEY_HARD_BUDGET = 'Hard Budget'
KEY_COST = 'Cost'
KEY_DURATION = 'Duration'
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
KEY_MET_COMMITMENT = 'Team Commitment'
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

# When a project passes its deadline/budget, management support decreases each week
OVERRUN_SUPPORT_MULTIPLIER = 0.995
COST_PER_DEV_RANK_DAY = 100
MAX_TEAM_SIZE = 6


# Placeholders, will be replaced with actual values when appropriate
budgetCoefficient = 5
deadlineCoefficient = 5
teamCoefficient = 2
codeCoefficient = 1
managementCoefficient = 5
softMetricCoefficients = { KEY_MET_COMMUNICATION: 5.0,
                            KEY_MET_COMMITMENT: 4.0,
                            KEY_MET_MORALE: 3.0,
                            KEY_MET_PLANNING: 4.0,
                            KEY_MET_SUPPORT: 2.0 }


# Given a project state, return the fraction of known bugs which have been resolved
def calc_proportion_bugs_resolved(state):
    resolved = state[KEY_CODE_BUGS_RESOLVED]
    total = state[KEY_CODE_BUGS_TOTAL]
    # Avoid divide by zero
    if total > 0:
        return float(resolved) / float(total)
    return 0


def calc_avg_team_rank(state):
    ranks = state[KEY_TEAM_RANKS]
    return np.mean(ranks) 


def status_to_string(status):
    if status == STATUS_CANCELLED:
        return "Cancelled"
    elif status == STATUS_COMPLETE:
        return "Complete"
    elif status == STATUS_PLANNING:
        return "Planning"
    else:
        return "Developing"


# Returns a randomly-generated float between 1 and 5, to 2.dp
def rand_metric_value():
    return round(SOFT_METRIC_MIN + random.random() * (SOFT_METRIC_MAX - SOFT_METRIC_MIN), 2)


# Logistic function to compress values into the range [0,1]
def sigmoid_func(x):
    k = 5       # Steepness
    x_0 = 1     # Centered around 1
    exp = math.exp(-k*(x-x_0))
    return 1 / (1+exp)


# Divides num by denom, then standardises with a logistic function
# Avoids dividing by zero
def calc_ratio_safe(num, denom):
    if denom > 0:
        return float(num) / float(denom)
    return 0


# All column headers for the state dataframe
metric_headers = [KEY_ID,KEY_BUDGET, KEY_DEADLINE, KEY_COST, KEY_DURATION, 
                  KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, 
                  KEY_MET_COMMUNICATION, KEY_MET_COMMITMENT, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                  KEY_TEAM_RANKS,KEY_TEAM_AVG_RANK, 
                  KEY_STATUS,KEY_PROGRESS]


# Columns which should be used as input for the prediction model 
independent_headers = [KEY_BUDGET, KEY_DEADLINE, KEY_COST, KEY_DURATION, 
                        KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, 
                        KEY_MET_COMMUNICATION, KEY_MET_COMMITMENT, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                        KEY_TEAM_AVG_RANK]



# Represents a simulated Project
class SimProject:
    rand = random

    def __init__(self, pid, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        self.statesDf = pd.DataFrame(columns=metric_headers)

        self.projectID = pid

        # Determines complexity and scale of the project (influencing team + budget)
        # TODO: change this back to between 1-10
        projectScale = random.randint(1,4) / 10.0

        softBdgt = self.generate_budget(minBudget, maxBudget, unitBudget, projectScale)
        softDl = self.generate_deadline(minDeadline, maxDeadline, projectScale)

        # Create an initial status for the project
        initRow = self.make_state(STATUS_PLANNING)
        initRow[KEY_BUDGET] = softBdgt
        initRow[KEY_DEADLINE] = softDl
        initRow[KEY_COST] = 0
        initRow[KEY_DURATION] = 0

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

        # Initialise soft metrics randomly
        initRow[KEY_MET_COMMUNICATION] = (round(avgRank, 2) + rand_metric_value()) / 2
        initRow[KEY_MET_PLANNING] = rand_metric_value()
        initRow[KEY_MET_COMMITMENT] = rand_metric_value()
        initRow[KEY_MET_SUPPORT] = rand_metric_value()
        initRow[KEY_MET_MORALE] = rand_metric_value()

        self.append_state(initRow)
        

    # Create a new blank project state (Dataframe row) with the given status
    def make_state(self, status):
        state = {
                    KEY_ID:self.projectID,
                    KEY_BUDGET:0, KEY_DEADLINE:0,
                    KEY_COST:0, KEY_DURATION:0, 
                    KEY_CODE_COMMITS:0, KEY_CODE_BUGS_TOTAL:0, KEY_CODE_BUGS_RESOLVED:0,
                    KEY_MET_COMMUNICATION:0, KEY_MET_COMMITMENT:0, KEY_MET_MORALE:0, KEY_MET_PLANNING:0, KEY_MET_SUPPORT:0,
                    KEY_TEAM_RANKS:[], KEY_TEAM_AVG_RANK:0,
                    KEY_PROGRESS: 0,
                    KEY_STATUS: status
                }

        return pd.Series(state)


    # Deep-copy the given row
    def copy_row(self, row):
        return pd.Series(row, copy=True)


    # Calculate the probability the next project state will be cancelled
    # Uses Exponential decay function
    def get_cancellation_chance(self, state):
        k = 20
        support_norm = state[KEY_MET_SUPPORT] / SOFT_METRIC_MAX
        return 0.5*math.exp(-k * support_norm)


    # Calculate the probability the next project state will have negative progress
    # Uses Exponential decay function
    def get_neg_progress_chance(self, state):
        k = 10
        morale_norm = state[KEY_MET_MORALE] / SOFT_METRIC_MAX
        return 0.2*math.exp(-k * morale_norm)


    def generate_budget(self, min, max, unitBudget, projScale):
        # Ideal cap on spending
        softBudget = self.rand.randint(min, max) * unitBudget
        # Absolute maximum spending permitted
        ##hardBudget = softBudget * (1 + math.pow(self.rand.random(), 2))
        return softBudget


    def generate_deadline(self, min, max, projScale):
        # Ideal deadline for project to be delivered by
        softDl = self.rand.randint(min, max)
        # Absolute latest project can be delivered by
        ##hardDl = softDl * (1 + math.pow(self.rand.random(), 2))
        return softDl

    
    # Retrieve the most recent project state
    def get_last_state(self):
        lst = len(self.statesDf) - 1
        return self.statesDf.iloc[lst]


    # Write a new state to the end of the dataframe
    def append_state(self, newState):
        self.statesDf = pd.concat([self.statesDf, newState.to_frame().T], ignore_index=True)


    # For the given state, add commits from the dev team and update the number of bugs
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
    # Note: there is a chance for the progress to decrease
    def update_progress(self, state, duration):
        comm = state[KEY_MET_COMMUNICATION]
        planning = state[KEY_MET_PLANNING]
        morale = state[KEY_MET_MORALE]

        # Apply log to reduce effect of large teams on progress
        teamsize = int(math.log(len(state[KEY_TEAM_RANKS])+1))

        delta = duration * ((comm + planning + morale) * teamsize / 3000) * (0.8 + 0.4 * random.random())

        # If any progress has been made on the project
        if state[KEY_PROGRESS] > 0:
            # Then, probabilistically reduce the progress
            if random.random() < self.get_neg_progress_chance(state):
                # Proportion of progress which is reversed (Square-Law to reduce effect)
                negProgress = pow(random.random(),2)
                delta = -negProgress * state[KEY_PROGRESS]
        
        # Update the progress, ensuring new value is no greater than 1
        state[KEY_PROGRESS] = min(1, state[KEY_PROGRESS] + delta)


    # Simulate the project's development, generating states until completion
    def simulate(self):
        dl = self.get_last_state()[KEY_DEADLINE]

        # Store newly-generated states in a list, so they can be added to the dataframe together
        newStates = []
        prevState = self.get_last_state()

        # Estimate the number of weeks spent planning
        weeksPlanning = int(prevState[KEY_MET_PLANNING]) * (0.75 + random.random() / 2)
        totalPlanningTime = weeksPlanning * 7

        # Days between state updates
        intervalLen = 1

        stopSim = False

        # Simulate project development until completion or cancellation
        while not stopSim:
            newState = self.copy_row(prevState)
            intervalCost = 0

            # If Planning Stage is complete
            if newState[KEY_STATUS] == STATUS_PLANNING:
                intervalCost = random.randint(0,500) * 7

                if newState[KEY_DURATION] >= totalPlanningTime:
                    newState[KEY_STATUS] = STATUS_DEVELOPING
            # If in development and the dev team contains at least one person
            elif newState[KEY_STATUS] == STATUS_DEVELOPING and len(newState[KEY_TEAM_RANKS]) > 0:
                self.add_commits_and_bugs(newState)

                # Calculate cost of paying development team for the interval
                for dev in newState[KEY_TEAM_RANKS]:
                    intervalCost += dev * COST_PER_DEV_RANK_DAY * intervalLen

                self.update_progress(newState, intervalLen)

                if newState[KEY_PROGRESS] >= 1:
                    newState[KEY_STATUS] = STATUS_COMPLETE
                    stopSim = True

            cancellation_chance = self.get_cancellation_chance(newState)
            if random.random() < cancellation_chance:
                newState[KEY_STATUS] = STATUS_CANCELLED
                stopSim = True

            # Every week the project overruns, the support of the executives decreases
            if newState[KEY_DURATION] > dl or newState[KEY_COST] > newState[KEY_BUDGET]:
                newState[KEY_MET_SUPPORT] *= OVERRUN_SUPPORT_MULTIPLIER

            newState[KEY_COST] += intervalCost
            newState[KEY_DURATION] += intervalLen
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


    # Adds a new final project state with the completed status
    def complete(self):
        lastState = self.get_last_state()
        completeState = self.make_state(STATUS_COMPLETE)
        if not lastState.empty:
            completeState = self.copy_row(lastState)
            completeState[KEY_STATUS] = STATUS_COMPLETE

        self.append_state(completeState)


    # Evaluate the success score of the project, by considering its last state
    def evaluate(self):
        lastState = self.get_last_state()
        return self.evaluate_state(lastState)


    # Retrieve the status of the last state of the project
    def get_status(self):
        if len(self.statesDf) > 0:
            lastState = self.get_last_state()
            return lastState[KEY_STATUS]
        return None

    # Convert project to string representation for debugging purposes
    def __str__(self):
        s = "Project w/ " + str(len(self.statesDf)) + " states:" + "\n"
        return s + str(self.statesDf)


    ## Project State Component Analysis
    # Each of these methods returns a float from 0 to 1
    def eval_budget(self, state):
        bdgtRatio = calc_ratio_safe(state[KEY_BUDGET], state[KEY_COST])
        return sigmoid_func(bdgtRatio)

    def eval_deadline(self, state):
        dlRatio = calc_ratio_safe(state[KEY_DEADLINE], state[KEY_DURATION])
        return sigmoid_func(dlRatio)

    # def eval_management(self, state):
    #     return state[KEY_MET_SUPPORT]

    def eval_code(self, state):
        return calc_proportion_bugs_resolved(state)

    def eval_team(self, state):
        totalTeamScore = 0
        maxPossScore = 0
        for (key, coeff) in softMetricCoefficients.items():
            totalTeamScore += coeff * state[key]
            maxPossScore += coeff * SOFT_METRIC_MAX
        return totalTeamScore / maxPossScore


    # For the given state, evaluate the overall success of the project in that state, 
    # returning a score between 0 and 1
    def evaluate_state(self, state):
        score = 0
        # Number of attributes included in the score
        maxScore = budgetCoefficient + deadlineCoefficient + teamCoefficient + codeCoefficient

        if state[KEY_STATUS] != STATUS_CANCELLED:
            budgetMeasure = self.eval_budget(state)
            deadlineMeasure = self.eval_deadline(state)
            teamMeasure = self.eval_team(state)
            codeMeasure = self.eval_code(state)

            # print("Budget:", budgetMeasure)
            # print("Deadline:", deadlineMeasure)
            # print("Team:", teamMeasure)
            # print("Code:", codeMeasure)

            score += budgetCoefficient * budgetMeasure
            score += deadlineCoefficient * deadlineMeasure
            score += teamCoefficient * teamMeasure
            score += codeCoefficient * codeMeasure

        ratioScore = score / maxScore
        # print(ratioScore)
        return ratioScore


    def get_dataframe(self):
        return self.statesDf


    def get_labelled_samples(self, k):
        # We can only take as many samples as there are states
        k = min(k, len(self.statesDf))
        sampleDf = self.statesDf.sample(k)

        successScore = self.evaluate()
        success = 0
        
        if successScore > 0.5:
            success = 1
        elif self.get_last_state()[KEY_STATUS] == STATUS_CANCELLED:
            success = -1
        
        sampleDf.insert(len(sampleDf.columns),'Success',success)
        # Remove the team ranks
        return sampleDf.drop(columns=[KEY_TEAM_RANKS],axis=1)



