from __future__ import print_function # In python 2.7
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response
from .model import RiskAssessmentGenerator as RAG
import pandas as pd
from .model import projectDf as SimProject
from .model.dataManipulation import calc_ratio_safe
from .gitLink import Git_Link as GitLinkObj
from sqlalchemy import func
import sys
import time

# Acts as an intermediate step between the website and the RiskAssessmentGenerator by 
# receiving a project ID and returning the RiskAssessment for that project.
# Retrieves all necessary data from the database and if data cannot be obtained, applies default values
# to ensure the ML can operate as intended.

# The default value for each of the team metrics, if they do not exist
#   (for example, if no survey responses in the db for a given project, then this value is used)
# This ensures the ML can still produce a meaningful output
SOFT_METRIC_DEFAULT = 3.0

class ProjectRiskInterface:

    def __init__(self):
        self.rag = RAG.RiskAssessmentGenerator()

    def get_risk_assessment(self, prjID):
        project = Project.query.filter_by(projectID = prjID).first()

        ## HARD METRICS
        # Get the most recent row of hard metrics for the given project
        newestHM = Hard_Metrics.query.filter_by(projectID = prjID).order_by(Hard_Metrics.date.desc()).first()
        currBudget = newestHM.budget
        currCost = newestHM.costToDate
        budgetElapsed = calc_ratio_safe(currCost, currBudget) 

        # Date of the most recent hard metric sample
        currDate = newestHM.date
        currDeadline = newestHM.deadline
        startDate = project.dateCreated
        daysElapsed = currDate - startDate
        daysDeadline = currDeadline - startDate
        # Calculate the proportion of the project time which has been used
        timeElapsed = calc_ratio_safe(daysElapsed, daysDeadline) 

        ## CODE METRICS
        # Retrieve the GitHub auth token and the URL of the repository from the database
        gitData = Git_Link.query.filter_by(projectID = prjID).first()
        if gitData != None:
            token = gitData.gitToken
            repoURL = gitData.repositoryURL
            gitLink = GitLinkObj(token, repoURL)
            # Get the code metrics from the project's repository
            numCommits = gitLink.getTotalCommits()
            defectFixRate = gitLink.getDefectFixRate()
        else:
            numCommits = 0
            defectFixRate = 0.0


        ## SUBDEADLINES
        # Get the number of this project's deadlines which are marked as "SUCCESS"
        metDeadlines = Deadline.query.filter_by(projectID = prjID, achieved=1).count()
        # Get the number of deadlines for this project
        final = Deadline.query.filter(Deadline.achieved >= 1, Deadline.projectID == prjID).count()

        if metDeadlines == None or final == None:
            proportionSubdeadlinesMet = 0.0
        else:
            proportionSubdeadlinesMet = calc_ratio_safe(metDeadlines, final)


        ## SOFT METRICS
        ## TODO - get the average for each soft metric for the last week of responses (note: must be labelled correctly)
        ## e.g. communicationAvg = ..., moraleAvg = ...
        #     * 'Team Communication'              - FLOAT in [1,5] (soft metric)
        #     * 'Team Commitment'                 - FLOAT in [1,5] (soft metric)
        #     * 'Team Morale'                     - FLOAT in [1,5] (soft metric)
        #     * 'Project Planning'                - FLOAT in [1,5] (soft metric)
        #     * 'Top-Level Management Support'    - FLOAT in [1,5] (soft metric)

        # Milliseconds in a week
        week = 7 * 24 * 60 * 60 * 1000
        # Find the interval over which the surveys will be averaged (i.e. the last week)
        endWindow = int(time.time())
        startWindow = endWindow - week
        avgCommunication = Survey_Response.query.with_entities(func.avg(Survey_Response.communicationMetric).label("avg_communication")).filter(Survey_Response.projectID == prjID, Survey_Response.date >= startWindow).all()
        print(avgCommunication, file=sys.stderr)
        teamCommunication = avgCommunication
        teamMorale = avgCommunication
        teamCommitment = avgCommunication
        teamSupport = avgCommunication
        projectPlanning = Worker.query.with_entities(func.avg(Worker.planning).label("avg_planning")).join(Works_On).filter(Works_On.projectID == prjID).scalar()
        
        if teamCommunication == None or teamCommunication == 0.0:
            teamCommunication = SOFT_METRIC_DEFAULT

        if teamCommitment == None or teamCommitment == 0.0:
            teamCommitment = SOFT_METRIC_DEFAULT

        if teamMorale == None or teamMorale == 0.0:
            teamMorale = SOFT_METRIC_DEFAULT

        if teamSupport == None or teamSupport == 0.0:
            teamSupport = SOFT_METRIC_DEFAULT

        if projectPlanning == None or projectPlanning == 0.0:
            projectPlanning = SOFT_METRIC_DEFAULT

        ## TEAM EXPERIENCE/SIZE
        avgTeamRank = Worker.query.with_entities(func.avg(Worker.experienceRank).label("avg_rank"))\
                                    .join(Works_On).filter_by(projectID = prjID).scalar()
        teamSize = Works_On.query.filter_by(projectID = prjID).count()

        # Must set a default value of 1 or more team members
        if teamSize == 0 or teamSize is None:
            teamSize = 1
            avgTeamRank = 1.0

        if avgTeamRank is None:
            avgTeamRank = 0.0

        # Construct a dictionary of the project values (so they can be converted to a Pandas series)
        projectStateDict = {}
        projectStateDict[SimProject.KEY_ID] = prjID
        projectStateDict[SimProject.KEY_BUDGET] = currBudget
        projectStateDict[SimProject.KEY_OVERALL_DEADLINE] = currDeadline
        projectStateDict[SimProject.KEY_TIME_ELAPSED] = timeElapsed
        projectStateDict[SimProject.KEY_BUDGET_ELAPSED] = budgetElapsed
        projectStateDict[SimProject.KEY_CODE_COMMITS] = numCommits
        projectStateDict[SimProject.KEY_CODE_BUGS_RESOLUTION] = defectFixRate
        projectStateDict[SimProject.KEY_SUBDEADLINES_MET_PROPORTION] = proportionSubdeadlinesMet
        projectStateDict[SimProject.KEY_TEAM_AVG_RANK] = avgTeamRank
        projectStateDict[SimProject.KEY_TEAM_SIZE] = teamSize

        ## Add the soft metrics here
        projectStateDict[SimProject.KEY_MET_COMMUNICATION] = 0 #teamCommunication
        projectStateDict[SimProject.KEY_MET_MORALE] = 0 #teamMorale
        projectStateDict[SimProject.KEY_MET_COMMITMENT] = 0 #teamCommitment
        projectStateDict[SimProject.KEY_MET_SUPPORT] = 0 #teamSupport
        projectStateDict[SimProject.KEY_MET_PLANNING] = 0 #projectPlanning

        projectState = pd.Series(projectStateDict)

        return self.rag.generate_ra(projectState)

