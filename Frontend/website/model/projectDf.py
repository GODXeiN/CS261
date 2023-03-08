import random
import math
import pandas as pd
import numpy as np

from .SuccessReport import *
from .dataManipulation import calc_ratio_safe, exponential, sigmoid_func

## Project-level metrics
KEY_ID = 'pID'
KEY_STATUS = 'Status'
KEY_PROGRESS = 'Progress'

## Hard metrics
KEY_BUDGET = 'Budget'
KEY_HARD_BUDGET = 'Hard Budget'
KEY_COST_TO_DATE = 'Cost'
KEY_DURATION = 'Duration'
KEY_OVERALL_DEADLINE = 'Overall Deadline'
# Float in range [0,1] representing Cost as a proportion of Budget
KEY_BUDGET_ELAPSED = 'Budget Elapsed'                       
# Float in range [0,1] representing proportion of overall deadline which has passed
KEY_TIME_ELAPSED = 'Time Elapsed'                           

## Internal project deadlines (development checkpoints)
# Number of deadlines which are upcoming
KEY_NUM_SUBDEADLINE_ACTIVE = 'Active Subdeadlines'      
# Number of internal deadlines for the entire project       
KEY_NUM_SUBDEADLINE_TOTAL = 'Total Subdeadlines'            
# Number of internal deadlines which have passed
KEY_NUM_SUBDEADLINE_EXPIRED = 'Expired Subdeadlines'        
# Number of expired internal deadlines which the project met the required progress
KEY_NUM_SUBDEADLINE_MET = 'Met Subdeadlines'                
# Float in range [0,1], representing (Met Subdeadlines) / (Expired Subdeadlines)
KEY_SUBDEADLINES_MET_PROPORTION = 'Proportion Subdeadlines Met' 

## Team metrics
KEY_TEAM_AVG_RANK = 'Average Team Experience'
KEY_TEAM_SIZE = 'Team Size'
KEY_TEAM_RANKS = 'Team Ranks'

## Soft metrics
KEY_MET_COMMUNICATION = 'Team Communication'
KEY_MET_MORALE = 'Team Morale'
KEY_MET_SUPPORT = 'Top-Level Management Support'
KEY_MET_PLANNING = 'Project Planning'
KEY_MET_COMMITMENT = 'Team Commitment'

## Code metrics
KEY_CODE_BUGS_TOTAL = 'Total Defects'
KEY_CODE_BUGS_RESOLVED = 'Fixed Defects'
## Float in range [0,1] representing (Resolved Bugs) / (Total Bugs)
KEY_CODE_BUGS_RESOLUTION = 'Defect Fix Rate'
KEY_CODE_COMMITS = 'Commits'

# Range of values for soft metrics 
SOFT_METRIC_MIN = 1
SOFT_METRIC_MAX = 5

STATUS_PLANNING = 0
STATUS_DEVELOPING = 1
STATUS_COMPLETE = 2
STATUS_CANCELLED = -1

# When a project passes its deadline/budget, management support decreases each week
OVERRUN_SUPPORT_MULTIPLIER = 0.999
# The base daily wage paid to a developer irrespective of their rank
BASE_COST_PER_DEV_DAY = 75
# The daily wage paid on top of the base cost
# e.g. a Rank 2 dev costs: 75 + 2 * 75/day = 150/day
#      a Rank 5 dev costs: 75 + 5 * 75/day = 450/day 
COST_PER_DEV_RANK_DAY = 75
# Maximum size of the team for a project of scale 1/10
TEAM_UNIT_SIZE = 6
# Maximum number of internal deadlines generated at the start of a project
MAX_INIT_SUBDEADLINES = 20
# Maximum number of times the project may overrun its deadline before it is cancelled
# This value helps to ensure projects are terminated
# e.g. if the project has an Overall Deadline of 100 days and MAX_TIMES_DEADLINE_ELAPSED = 3, 
#           then the project will be cancelled at day 301
MAX_TIMES_DEADLINE_ELAPSED = 3
MAX_BUGS_PER_COMMIT = 20

# Placeholders, will be replaced with actual values when appropriate
softMetricCoefficients = { KEY_MET_COMMUNICATION: 1.0,
                            KEY_MET_COMMITMENT: 1.5,
                            KEY_MET_MORALE: 2.0 }


# All column headers for the state dataframe
metric_headers = [KEY_ID, 
                  KEY_BUDGET, KEY_COST_TO_DATE, KEY_BUDGET_ELAPSED,
                  KEY_OVERALL_DEADLINE, KEY_DURATION, KEY_TIME_ELAPSED, 
                  KEY_NUM_SUBDEADLINE_TOTAL, KEY_NUM_SUBDEADLINE_MET, KEY_SUBDEADLINES_MET_PROPORTION,
                  KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLVED, KEY_CODE_BUGS_TOTAL, KEY_CODE_BUGS_RESOLUTION ,
                  KEY_MET_COMMUNICATION, KEY_MET_COMMITMENT, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                  KEY_TEAM_RANKS, KEY_TEAM_AVG_RANK, KEY_TEAM_SIZE, 
                  KEY_STATUS, KEY_PROGRESS]


# Columns which should be used as input for the prediction model 
independent_headers = [KEY_BUDGET, KEY_OVERALL_DEADLINE, KEY_BUDGET_ELAPSED, KEY_TIME_ELAPSED, 
                        KEY_SUBDEADLINES_MET_PROPORTION,
                        KEY_CODE_COMMITS, KEY_CODE_BUGS_RESOLUTION, 
                        KEY_MET_COMMUNICATION, KEY_MET_COMMITMENT, KEY_MET_MORALE, KEY_MET_PLANNING, KEY_MET_SUPPORT,
                        KEY_TEAM_AVG_RANK, KEY_TEAM_SIZE]



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


# Represents a simulated Project
class SimProject:
    rand = random

    def add_initial_sub_deadlines(self, initRow):
        # Controls the distribution of the number of subdeadlines
        # (steeper gradient = fewer projects with more deadlines)
        FREQUENCY_GRADIENT = 2
        # Generate an exponentially distributed float [0,1]
        subdeadlines_float = exponential(random.random(), FREQUENCY_GRADIENT, 1, 0)
        initRow[KEY_NUM_SUBDEADLINE_TOTAL] = int(MAX_INIT_SUBDEADLINES * subdeadlines_float)

        # print(initRow[KEY_NUM_SUBDEADLINE_TOTAL])

        startDate = 0
        endDate = initRow[KEY_OVERALL_DEADLINE]
        projectDuration = endDate - startDate
        subdeadlines = []

        # Equally space deadline within the project's timeframe
        # The number of gaps is one more than the number of deadlines
        intervalBetweenDeadlines = int(projectDuration / (initRow[KEY_NUM_SUBDEADLINE_TOTAL] + 1))

        # We want some randomness in the deadline dates, but we need to ensure they balance out over the entire project
        # Therefore, we keep the last "extension" amount and use it to shrink the next deadline
        lastRandomExtensionAmt = 0

        # Generate the deadlines and the progress expected by that point in the project
        for i in range(0, initRow[KEY_NUM_SUBDEADLINE_TOTAL]):
            dlDay = startDate + intervalBetweenDeadlines

            if lastRandomExtensionAmt > 0:
                dlDay -= lastRandomExtensionAmt
                lastRandomExtensionAmt = 0
            else:
                lastRandomExtensionAmt = random.randint(0, int(projectDuration / 20))
                dlDay += lastRandomExtensionAmt

            expectedProgress = dlDay / endDate
            startDate = dlDay + 1

            # Only add the subdeadline if it is before the overall deadline (100% completion)
            if expectedProgress < 1 and dlDay < endDate:
                # Store subdeadlines as a tuple, representing the target day, and the expected progress in the range [0,1]
                subdeadlines.append((dlDay, expectedProgress))


        self.active_subdeadlines = subdeadlines
        # print("Generated Subdeadlines:", str(subdeadlines))
        initRow[KEY_NUM_SUBDEADLINE_ACTIVE] = len(subdeadlines)


    def __init__(self, pid, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        self.statesDf = pd.DataFrame(columns=metric_headers)

        self.projectID = pid

        # Determines complexity and scale of the project
        projectScale = random.randint(1,10) / 10.0

        softBdgt = self.generate_budget(minBudget, maxBudget, unitBudget, projectScale)
        softDl = self.generate_deadline(minDeadline, maxDeadline, projectScale)

        # Create an initial status for the project
        initRow = self.make_state(STATUS_PLANNING)
        initRow[KEY_BUDGET] = softBdgt
        initRow[KEY_OVERALL_DEADLINE] = softDl
        initRow[KEY_COST_TO_DATE] = 0
        initRow[KEY_DURATION] = 0

       
        max_team_size = TEAM_UNIT_SIZE * 10 * projectScale

        # Generate the development ranks for a random team
        # A larger project is permitted to have a larger dev team (but not required to)
        teamRanks = []
        # Exponentially-distributed team sizes (+1 to ensure at least one team member)
        teamSize = int(round(max_team_size * exponential(random.random(), 3, 1, 0))) + 1
        # print(teamSize)
        totalRank = 0
        # Generate the ranks for the team members arbitrarily (and keep a running sum to calculate the average)
        for i in range(0, teamSize):
            rank = random.randint(1,5)
            teamRanks.append(rank)
            totalRank += rank

        avgRank = totalRank / teamSize
        initRow[KEY_TEAM_AVG_RANK] = avgRank
        initRow[KEY_TEAM_RANKS] = teamRanks
        initRow[KEY_TEAM_SIZE] = teamSize

        self.add_initial_sub_deadlines(initRow)

        # Initialise soft metrics randomly
        initRow[KEY_MET_COMMUNICATION] = rand_metric_value()
        initRow[KEY_MET_PLANNING] = rand_metric_value()
        initRow[KEY_MET_COMMITMENT] = rand_metric_value()
        initRow[KEY_MET_SUPPORT] = rand_metric_value()
        initRow[KEY_MET_MORALE] = rand_metric_value()

        self.append_state(initRow)
        


    # Create a new blank project state (Dataframe row) with the given status
    def make_state(self, status):
        state = {
                    KEY_ID:self.projectID,
                    KEY_BUDGET:0, KEY_COST_TO_DATE:0, KEY_BUDGET_ELAPSED:0.0,
                    KEY_OVERALL_DEADLINE:0, KEY_DURATION:0, KEY_TIME_ELAPSED:0.0,
                    KEY_NUM_SUBDEADLINE_TOTAL:0, KEY_NUM_SUBDEADLINE_MET:0, KEY_SUBDEADLINES_MET_PROPORTION:0.0,
                    KEY_NUM_SUBDEADLINE_ACTIVE:0, KEY_NUM_SUBDEADLINE_EXPIRED:0,
                    KEY_CODE_COMMITS:0, KEY_CODE_BUGS_TOTAL:0, KEY_CODE_BUGS_RESOLVED:0, KEY_CODE_BUGS_RESOLUTION:0.0,
                    KEY_MET_COMMUNICATION:0, KEY_MET_COMMITMENT:0, KEY_MET_MORALE:0, KEY_MET_PLANNING:0, KEY_MET_SUPPORT:0,
                    KEY_TEAM_RANKS:[], KEY_TEAM_AVG_RANK:0, KEY_TEAM_SIZE:0,
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
        k = -20
        # Get support metric as a float in the range [0,1]
        support = state[KEY_MET_SUPPORT] / SOFT_METRIC_MAX
        return 0.5 * exponential(support, k, 0, 0)


    # Calculate the probability the next project state will have negative progress
    # Uses Exponential decay function
    def get_neg_progress_chance(self, state):
        k = -10
        # Get morale metric in range [0,1]
        morale = state[KEY_MET_MORALE] / SOFT_METRIC_MAX
        return 0.2 * exponential(morale, k, 0, 0)


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
    def add_commits_and_bugs(self, state, intervalLen):
        devTeam = state[KEY_TEAM_RANKS]

        # Number of commits is proportional to the morale and dev team size
        newCommits = 0
        newBugs = 0
        newResolvedBugs = 0

        # Get the number of unresolved bugs in the codebase
        existingBugs = state[KEY_CODE_BUGS_TOTAL] - state[KEY_CODE_BUGS_RESOLVED]

        morale = state[KEY_MET_MORALE]

        # Consider each member of the team in-turn
        for experience in devTeam:
            # Maximum possible commits per day for each development member 
            # is based on the commitment of the team to the project with some randomness
            MAX_POSSIBLE_COMMITS = int(state[KEY_MET_COMMITMENT] * 0.75) + random.randint(0,2)

            # For each day in the elapsed interval
            for d in range (0, intervalLen):
                effort = (0.75 * (morale / SOFT_METRIC_MAX) + 0.25 * random.random())
                # Generate a number of new commits based on the morale of the developer
                newDevCommits = int(round(MAX_POSSIBLE_COMMITS * exponential(effort, 2, 1, 0))) + 1
                # print(newDevCommits)

                # print("New Commits: ", newDevCommits)
                newCommits += newDevCommits

                # Each commit has bugs but some of these may be solved by the developer.
                # Now, we calculate the chance of a developer not fixing a bug, 
                #   inversely related to their experience e.g.
                #       a Rank-0 dev has a 75% chance of introducing a bug; 
                #       a Rank-5 dev has a 30% chance of introducing a bug

                # Get estimate of team member reliability (0-1), which is assumed to be 
                # inversely related to the likelihood of bug creation
                reliability = (experience + state[KEY_MET_COMMITMENT]) / (2 * SOFT_METRIC_MAX)
                bugLikelihood = 0.75 * exponential(reliability, -1, 0, 0)

                # Generate some random number of bugs
                commitBugs = 0
                for i in range(0, newDevCommits):
                    if random.random() < bugLikelihood:
                        commitBugs += int(MAX_BUGS_PER_COMMIT * exponential(random.random(), 2, 1, 0))
                        
                newBugs += commitBugs
                # print("Bugs:",commitBugs)

                # Fix some number of bugs
                commitResolvedBugs = random.randint(0, commitBugs)
                # Bugs which already exist in the code may be solved
                if existingBugs > 0:
                    existingResolvedBugs = random.randint(0, existingBugs)
                    existingBugs -= existingResolvedBugs
                    newResolvedBugs += existingResolvedBugs

                newResolvedBugs += commitResolvedBugs

        state[KEY_CODE_COMMITS] += newCommits
        state[KEY_CODE_BUGS_TOTAL] += newBugs
        state[KEY_CODE_BUGS_RESOLVED] += newResolvedBugs


    # Set the new progress of the project, based on the team's soft metrics
    # Note: there is a chance for the progress to decrease
    def update_progress(self, state, duration):
        comm = state[KEY_MET_COMMUNICATION]
        planning = state[KEY_MET_PLANNING]
        morale = state[KEY_MET_MORALE]

        # Apply log to limit the effect of large teams on the progress
        teamsize = int(math.log(state[KEY_TEAM_SIZE]+1))

        avgMetric = (comm + planning + morale) / 15

        delta = duration * (avgMetric * teamsize / 100) * (0.8 + 0.4 * random.random())

        # If any progress has been made on the project
        if state[KEY_PROGRESS] > 0:
            # Then, there is a chance that the team will lose progress (maybe due to a problem)
            if random.random() < self.get_neg_progress_chance(state):
                # Proportion of progress which is reversed (Square-Law to reduce effect)
                negProgress = pow(random.random() / 2, 2)
                delta = -negProgress * state[KEY_PROGRESS]
                # print("Negative Progress:", str(delta))
        
        # Update the progress, ensuring new value is no greater than 1
        state[KEY_PROGRESS] = min(1, state[KEY_PROGRESS] + delta)



    # Check if we've passed (met or missed) any internal deadlines, and if so,
    # make them no longer active and record the result of the deadline
    def checkForExpiredDeadlines(self, state):
        activeDeadlines = self.active_subdeadlines
        currentProgress = state[KEY_PROGRESS]
        currentDay = state[KEY_DURATION]
        current = (currentDay, currentProgress)

        while len(activeDeadlines) > 0:
            # Get the day of the deadline and the expected progress
            subdl = activeDeadlines[0]
            (dlDay, expProgress) = subdl

            # If the project has passed the deadline's required progress
            if currentProgress >= expProgress:
                # Remove the deadline which was met from the Active list
                activeDeadlines.pop(0)
                state[KEY_NUM_SUBDEADLINE_ACTIVE] -= 1
                # Record that a deadline passed AND was met
                state[KEY_NUM_SUBDEADLINE_EXPIRED] += 1
                state[KEY_NUM_SUBDEADLINE_MET] += 1
                # print("Met a subdeadline")

            # Otherwise, if progress is insufficient and the deadline has passed 
            elif currentDay >= dlDay:
                # Remove the deadline which has expired from the active list
                activeDeadlines.pop(0)
                state[KEY_NUM_SUBDEADLINE_ACTIVE] -= 1
                # Record that a deadline passed
                state[KEY_NUM_SUBDEADLINE_EXPIRED] += 1
               
            # Otherwise, stop checking, as the next deadline is still in the future but hasn't been met yet
            else:
                break

        


    # Calculates the cost of paying development team for the given interval and adds that
    # amount to the cumulative cost of the project
    def include_team_costs(self, state, intervalLen):
        for dev in state[KEY_TEAM_RANKS]:
            state[KEY_COST_TO_DATE] += dev * COST_PER_DEV_RANK_DAY * intervalLen


    def include_unforeseen_costs(self, state, intervalLen):
        # In software development, projects usually encounter costs which were not
        # expected, for example with infrastructure upgrades or new technologies.
        # This function simulates the chance for the project to encounter one of these costs

        planning = state[KEY_MET_PLANNING]/SOFT_METRIC_MAX
        # A well-planned project is less likely to encounter additional costs (but still can do so)

        # Calculate the probability of incurring costs (between 0.05 and 0.5)
        probIncurCosts = 0.1 * exponential(planning, -1, 0, 0.05)

        maxCost = 10000     # Maximum possible cost
        baseCost = 0.01    # Minimum possible cost, as a proportion of the maximum cost

        costK = 5          # Steepness of exponential cost function 

        # Every day, the project has a 1% chance to encounter additional costs
        for i in range(0, intervalLen):
            if random.random() < probIncurCosts:
                x = random.random()
                # Generate an exponentially-distributed cost, rounding to ensure integer value
                unforeseenCost = int(maxCost * (exponential(x, costK, 1, baseCost)))
                # print("Unforeseen Cost:", str(unforeseenCost))
                state[KEY_COST_TO_DATE] += unforeseenCost


    # Simulate the project's development, generating states until completion
    def simulate(self):
        dl = self.get_last_state()[KEY_OVERALL_DEADLINE]

        # Store newly-generated states in a list, so they can be added to the dataframe together
        newStates = []
        prevState = self.get_last_state()

        # Estimate the number of weeks spent planning
        weeksPlanning = int(prevState[KEY_MET_PLANNING]) * (0.75 + random.random() / 2)
        totalPlanningTime = weeksPlanning * 7

        # Number of days between state updates
        intervalLen = 1

        stopSim = False

        # Simulate project development until completion or cancellation
        while not stopSim:
            newState = self.copy_row(prevState)

            newState[KEY_DURATION] += intervalLen

            # If project is being planned
            if newState[KEY_STATUS] == STATUS_PLANNING:
                # Add some arbitrary planning costs
                newState[KEY_COST_TO_DATE] += random.randint(10,100) * intervalLen

                # If planning is complete, move to development
                if newState[KEY_DURATION] >= totalPlanningTime:
                    newState[KEY_STATUS] = STATUS_DEVELOPING

            # Otherwise, if in development and the dev team contains at least one person
            elif newState[KEY_STATUS] == STATUS_DEVELOPING and len(newState[KEY_TEAM_RANKS]) > 0:
                self.add_commits_and_bugs(newState, intervalLen)
                newState[KEY_CODE_BUGS_RESOLUTION] = calc_ratio_safe(newState[KEY_CODE_BUGS_RESOLVED], newState[KEY_CODE_BUGS_TOTAL])

                self.include_team_costs(newState, intervalLen)
                self.include_unforeseen_costs(newState, intervalLen)
                self.update_progress(newState, intervalLen)

                # If the project is fully complete, stop the simulation
                if newState[KEY_PROGRESS] >= 1:
                    newState[KEY_STATUS] = STATUS_COMPLETE
                    stopSim = True

                self.checkForExpiredDeadlines(newState)

            cancellation_chance = self.get_cancellation_chance(newState)
            # If the project is chosen by the management to be cancelled 
            # or it has significantly overrun its original deadline, then it is cancelled and the simulation stopped
            if random.random() < cancellation_chance or newState[KEY_TIME_ELAPSED] >= MAX_TIMES_DEADLINE_ELAPSED:
                newState[KEY_STATUS] = STATUS_CANCELLED
                stopSim = True

            # Every week the project overruns, the support of the executives decreases
            if newState[KEY_DURATION] > dl or newState[KEY_COST_TO_DATE] > newState[KEY_BUDGET]:
                newState[KEY_MET_SUPPORT] *= OVERRUN_SUPPORT_MULTIPLIER

            # Calculate Total Cost as a fraction of the Budget 
            newState[KEY_BUDGET_ELAPSED] = calc_ratio_safe(newState[KEY_COST_TO_DATE], newState[KEY_BUDGET])
            # Calculate Project Duration as a fraction of the Deadline
            newState[KEY_TIME_ELAPSED] = calc_ratio_safe(newState[KEY_DURATION], newState[KEY_OVERALL_DEADLINE])
            # Calculate proportion of Expired Internal Deadlines which were Met
            newState[KEY_SUBDEADLINES_MET_PROPORTION] = calc_ratio_safe(newState[KEY_NUM_SUBDEADLINE_MET], newState[KEY_NUM_SUBDEADLINE_EXPIRED])

            # print(str(newState[KEY_NUM_SUBDEADLINE_MET]) + "/" + str(newState[KEY_NUM_SUBDEADLINE_EXPIRED]) + "=" + str(newState[KEY_SUBDEADLINES_MET_PROPORTION]))

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

    # Metrics Used: Budget; CostToDate
    def eval_finance(self, state):
        # surplusCost = state[KEY_COST_TO_DATE] - state[KEY_BUDGET]  
        # print("Budget:", state[KEY_BUDGET])
        # print("Cost:", state[KEY_COST_TO_DATE])
        # print("Surplus:",str(surplusCost))
        
        # # If project costs total to more than budget, then the project overspent
        # if surplusCost > 0:
        #     # Calculate the overspending as a proportion of the initial budget [0,infinity]
        #     ospendFactor = calc_ratio_safe(surplusCost, state[KEY_BUDGET])
        #     # print("Overspending by ", str(round(ospendFactor,2)) + " of budget")
        #     # Apply exponential decay to the evaluation to return a value in the range [0,0.5]
        #     eval = 0.5 * exponential(ospendFactor, -1, 0, 0)
        #     # print("Overspending Eval:", str(eval))
        #     return eval
        # # Otherwise, project is on/under budget
        # else:
        #     # Calculate the savings as a proportion of the budget (i.e. a value in the range [0,1])
        #     # Note: since -cost <= budget, we have a max factor of 1
        #     uspendFactor = calc_ratio_safe(-surplusCost, state[KEY_BUDGET])
        #     print("Underspending by ", str(round(uspendFactor,2)) + " of budget")
        #     # Apply Sigmoid Function 
        #     eval = sigmoid_func(uspendFactor, -5, 0)
        #     print("Underspending Eval:", str(eval))
        #     return eval
        
        # Calculate a measure of spending, a value in range [0, infinity]
        # If the project is on-budget, then this value is 1
        # If the project is under-budget, then this value is >1
        # If the project is over-budget, then this value is in range [0,1)
        spendingFactor = calc_ratio_safe(state[KEY_BUDGET], state[KEY_COST_TO_DATE])
        # Apply a flipped sigmoid function to produce an evaluation in the range [0,1]
        # Higher inputs (under-budget) produce a higher output (more success); 
        # Inputting 1 yields 0.5 (neutral success)
        return sigmoid_func(spendingFactor, -5, 1)

    # Metrics Used: Deadline; Duration
    def eval_time(self, state):
        timeFactor = calc_ratio_safe(state[KEY_OVERALL_DEADLINE], state[KEY_DURATION])
        # Compress the time factor into the range [0,1]
        timeNormalised = sigmoid_func(timeFactor, -5, 0) 
        # Calculate the proportion of passed subdeadlines which were met
        subDlRatio = calc_ratio_safe(state[KEY_NUM_SUBDEADLINE_MET], state[KEY_NUM_SUBDEADLINE_EXPIRED])
        # print("Sub DL Ratio:", str(subDlRatio))
        # print(subDlRatio)
        return (timeNormalised + subDlRatio) / 2

    # Metrics Used: Top-Level Management Support; Project Planning
    def eval_management(self, state):
        supportPlusPlanning = (state[KEY_MET_SUPPORT] + state[KEY_MET_PLANNING]) / (2 * SOFT_METRIC_MAX)
        return supportPlusPlanning

    # Metrics Used: CommitFrequency; ResolvedBugs; TotalBugs
    def eval_code(self, state):
        # Get an estimate for project activity by considering commit frequency 
        # before and after the last 30 days. Apply Sigmoid to restrict to the range [0,1]
        activityRatio = sigmoid_func(self.get_activity_ratio(30), -5, 1)
        # print("Activity Ratio:", str(activityRatio))
        # Consider the proportion of *known* bugs which have been resolved
        resolvedBugRatio = calc_proportion_bugs_resolved(state)
        return (activityRatio + resolvedBugRatio) / 2

    # Metrics Used: Team Commitment; Team Morale; Team Confidence 
    def eval_team(self, state):
        totalTeamScore = 0
        maxPossScore = 0
        # Consider the weighted sum of all soft team metrics
        for (key, coeff) in softMetricCoefficients.items():
            totalTeamScore += coeff * (state[key] / SOFT_METRIC_MAX)
            maxPossScore += coeff
        return totalTeamScore / maxPossScore


    # For the given state, evaluate the success of each of the major components and then the overall project
    def evaluate_state(self, state):
        succReport = SuccessReport.SuccessReport()

        if state[KEY_STATUS] != STATUS_CANCELLED:
            budgetMeasure = self.eval_finance(state)
            deadlineMeasure = self.eval_time(state)
            teamMeasure = self.eval_team(state)
            codeMeasure = self.eval_code(state)
            managementMeasure = self.eval_management(state)

            succReport.set_success_values(budgetMeasure, deadlineMeasure, teamMeasure, codeMeasure, managementMeasure)            

        return succReport


    def get_dataframe(self):
        return self.statesDf


    # Calculate the number of commits per day, for the last D days from the end of the project
    def get_commit_frequency(self, D):
        lastState = self.get_last_state()
        today = lastState[KEY_DURATION]

        # Calculate commit frequency for the entire project
        if D == 0:
            return calc_ratio_safe(lastState[KEY_CODE_COMMITS], lastState[KEY_DURATION])
        # Only consider commits over the last D days 
        else:
            commitsInInterval = lastState[KEY_CODE_COMMITS]
            # Find the first state outside the chosen interval
            for i in range(len(self.statesDf)-1, 0):
                state = self.statesDf.iloc[i]
                # If more than D days between this state and the most-recent state
                if state[KEY_DURATION] + D < today:
                    commitsInInterval -= state[KEY_CODE_COMMITS]
                    break

            return calc_ratio_safe(commitsInInterval, D)


    # Calculate the commit frequency for the interval ending D days ago, then for the interval starting D days ago 
    # and ending at the most-recent state. Return the ratio of the second frequency over the first frequency.
    def get_activity_ratio(self, D):
        lastState = self.get_last_state()
        today = lastState[KEY_DURATION]

        commitsBefore = 0
        daysBefore = 0

        for i in range(0, len(self.statesDf)):
            state = self.statesDf.iloc[i]
            # If more than D days between this state and the most-recent state
            if state[KEY_DURATION] + D >= today:
                break
            else:
                commitsBefore = state[KEY_CODE_COMMITS]
                daysBefore = state[KEY_DURATION]
        
        commitsAfter = lastState[KEY_CODE_COMMITS] - commitsBefore
        daysAfter = lastState[KEY_DURATION] - daysBefore

        commFreqBefore = calc_ratio_safe(commitsBefore, daysBefore)
        commFreqAfter = calc_ratio_safe(commitsAfter, daysAfter)

        return calc_ratio_safe(commFreqAfter, commFreqBefore)
 




    def get_labelled_samples(self, k):
        headersToWrite = []
        headersToWrite.append(KEY_ID)
        headersToWrite.extend(independent_headers)

        # We can only take as many samples as there are states
        k = min(k, len(self.statesDf))
        sampleDf = self.statesDf.sample(k, ignore_index=True)[headersToWrite]

        # Evaluate whether the project was a success, producing a score in range [0,1] for each component
        successReport = self.evaluate()

        # Binarize each success value to 0 or 1
        binarySuccesses = successReport.get_binary_successes()

        # Insert each success value as a new column in the sampled data-points
        sampleDf.insert(len(sampleDf.columns), 'Finance Success', binarySuccesses[SuccessReport.KEY_FINANCE])
        sampleDf.insert(len(sampleDf.columns), 'Timescale Success', binarySuccesses[SuccessReport.KEY_TIMESCALE])
        sampleDf.insert(len(sampleDf.columns), 'Team Success', binarySuccesses[SuccessReport.KEY_TEAM])
        sampleDf.insert(len(sampleDf.columns), 'Management Success', binarySuccesses[SuccessReport.KEY_MANAGEMENT])
        sampleDf.insert(len(sampleDf.columns), 'Code Success', binarySuccesses[SuccessReport.KEY_CODE])
        sampleDf.insert(len(sampleDf.columns), 'Success', binarySuccesses[SuccessReport.KEY_OVERALL])

        # Remove the team ranks
        return sampleDf


