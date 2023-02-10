import random
import math

KEY_BUDGET = 'Budget'
KEY_HARD_BUDGET = 'Hard Budget'
KEY_COST = 'Cost'
KEY_DAYS = 'Duration'
KEY_DEADLINE = 'Deadline'
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


# Status (snap-shot) of a project at a given point in its development
# Implements Prototype Design Pattern (clone for easy duplication)
class ProjectStatus:
    def __init__(self, status):
        self.featureDict = {}

        self.featureDict[KEY_STATUS] = status

        self.featureDict[KEY_TEAM_SIZE] = 0
        self.featureDict[KEY_TEAM_RANKS] = []
        
        # Project Hard Metrics
        self.featureDict[KEY_BUDGET] = 0
        self.featureDict[KEY_COST] = 0
        self.featureDict[KEY_DAYS] = 0
        self.featureDict[KEY_DEADLINE] = 0

        # Soft Metrics (mean from surveys)
        self.featureDict[KEY_MET_COMMUNICATION] = 0
        self.featureDict[KEY_MET_MORALE] = 0
        self.featureDict[KEY_MET_SUPPORT] = 0
        self.featureDict[KEY_MET_CONFID] = 0
        self.featureDict[KEY_MET_PLANNING] = 0

        # Code Metrics
        self.featureDict[KEY_CODE_BUGS_RESOLVED] = 0
        self.featureDict[KEY_CODE_BUGS_TOTAL] = 0
        self.featureDict[KEY_CODE_COMMITS] = 0

    def set_feature(self, key, val):
        if key in self.featureDict:
            self.featureDict[key] = val
        else:
            print("Error: attempt to add new key (" + str(key) + ") to feature dictionary") 

    def get_feature(self, key):
        if key in self.featureDict:
            return self.featureDict[key]
        return None

    def get_avg_team_rank(self):
        ranks = self.featureDict[KEY_TEAM_RANKS]
        totalRank = 0
        for rank in ranks:
            totalRank += rank
        return totalRank / self.featureDict[KEY_TEAM_SIZE]   

    def __repr__(self):
        s = "{"
        for (key, val) in self.featureDict.items():
            s += "    " + key + ": " + str(val) + "\n"
        return s + "}"

    # Creates a deep-copy of this status
    def clone(self):
        clone = ProjectStatus(self.get_feature(KEY_STATUS))
        for (key, val) in self.featureDict.items():
            clone.set_feature(key, val.copy())    
        return clone 

    def set_status(self, newStatus):
        self.set_feature(KEY_STATUS, newStatus)


class Project:
    rand = random

    def __init__(self):
        self.states = []
        return None

    def generateBudget(self, min, max, unitBudget):
        # Ideal cap on spending
        softBudget = self.rand.randint(min, max) * unitBudget
        # Absolute maximum spending permitted
        hardBudget = softBudget * (1 + math.pow(self.rand.random(), 2))
        return (softBudget, hardBudget)

    def generateDeadline(self, min, max):
        # Ideal deadline for project to be delivered by
        softDl = self.rand.randint(min, max)
        # Absolute latest project can be delivered by
        hardDl = softDl * (1 + math.pow(self.rand.random(), 2))
        return (softDl, hardDl)
        
    def make(self, minBudget, maxBudget, unitBudget, minDeadline, maxDeadline):
        initState = ProjectStatus(STATUS_ONGOING)
        (softBdgt, hardBdgt) = self.generateBudget(minBudget, maxBudget, unitBudget)
        (softDl, hardDl) = self.generateDeadline(minDeadline, maxDeadline)
        initState.set_feature(KEY_BUDGET, softBdgt)
        initState.set_feature(KEY_DEADLINE, softDl)
        self.states.append(initState)

    def get_last_state(self):
        if self.states > 0:
            return self.states[len(self.states)-1]
        return None

    # Adds a new final project state with the cancelled status
    def cancel(self):
        lastState = self.get_last_state()
        cancelState = None

        if lastState == None:
            cancelState = ProjectStatus(STATUS_CANCELLED)
        else:
            cancelState = lastState.clone()
            cancelState.set_feature(KEY_STATUS, STATUS_CANCELLED)

        self.states.append(cancelState)
        return cancelState

    def __str__(self):
        s = "Project w/ " + str(len(self.states)) + " states:" + "\n"
        return s + str(self.states)




