from __future__ import print_function # In python 2.7

from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response
from .model import RiskAssessmentGenerator as RAG
import pandas as pd
from .model import projectDf as SimProject
from .model.logregTrainer import CSV_TRAINING_DATA
from .model.modelCrossTrainer import train_all_models
from .model import SuccessReport
from .model.dataManipulation import calc_ratio_safe
from .gitLink import Git_Link as GitLinkObj
from sqlalchemy import func
import time
import sys

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
        state = self.get_project_state(prjID)
        return self.rag.generate_ra(state)


    # Get the most-recent state for the project
    def get_project_state(self, prjID):
        project = Project.query.filter_by(projectID = prjID).first()

        ## HARD METRICS
        # Get the most recent row of hard metrics for the given project
        newestHM = Hard_Metrics.query.filter_by(projectID = prjID).order_by(Hard_Metrics.date.desc()).first()
        currBudget = newestHM.budget
        currCost = newestHM.costToDate
        budgetElapsed = calc_ratio_safe(currCost, currBudget) 

        # Date of the most recent hard metric sample in UNIX time
        currDate = newestHM.date
        deadlineDate = newestHM.deadline
        startDate = project.dateCreated
        # Seconds since project started
        durationTS = currDate - startDate

        secondsPerDay = 24 * 3600
        # Days since project started
        durationDays = int(durationTS / secondsPerDay)
        # Seconds for project deadline
        deadlineTS =  deadlineDate - startDate
        # Days for project deadline
        deadlineDays = int(deadlineTS / secondsPerDay)
        # Calculate the proportion of the project time which has been used
        timeElapsed = calc_ratio_safe(durationDays, deadlineDays) 

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
        # Get the number of completed (not ongoing) deadlines for this project
        completedDeadlines = Deadline.query.filter(Deadline.achieved >= 1, Deadline.projectID == prjID).count()

        if metDeadlines == None or completedDeadlines == None:
            proportionSubdeadlinesMet = 0.0
        else:
            proportionSubdeadlinesMet = calc_ratio_safe(metDeadlines, completedDeadlines)


        ## SOFT METRICS
        # Seconds in a week
        week = 7 * secondsPerDay
        # Find the interval over which the surveys will be averaged (i.e. the last week)
        endWindow = int(time.time())
        startWindow = endWindow - week
        ## Get the average for each soft metric for the last week of responses (note: must be labelled correctly)
        teamCommunication = Survey_Response.query.with_entities(func.avg(Survey_Response.communicationMetric).label("avg_communication")).filter(Survey_Response.projectID == prjID, Survey_Response.date >= startWindow).scalar()
        teamMorale = Survey_Response.query.with_entities(func.avg(Survey_Response.happinessMetric).label("avg_morale")).filter(Survey_Response.projectID == prjID, Survey_Response.date >= startWindow).scalar()
        teamCommitment = Survey_Response.query.with_entities(func.avg(Survey_Response.commitmentMetric).label("avg_commitment")).filter(Survey_Response.projectID == prjID, Survey_Response.date >= startWindow).scalar()
        teamSupport = Survey_Response.query.with_entities(func.avg(Survey_Response.managementMetric).label("avg_management")).filter(Survey_Response.projectID == prjID, Survey_Response.date >= startWindow).scalar()
        projectPlanning = Worker.query.with_entities(func.avg(Worker.planning).label("avg_planning")).join(Works_On).filter(Works_On.projectID == prjID).scalar()
        
        # If project has no surveys, then the average may be None, but the model requires numeric data
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
        if teamSize == 0 or teamSize is None or avgTeamRank is None:
            teamSize = 1
            avgTeamRank = 1.0

        # Construct a dictionary of the project values (so they can be converted to a Pandas series)
        projectStateDict = {
            SimProject.KEY_ID: prjID,
            SimProject.KEY_BUDGET: currBudget,
            SimProject.KEY_OVERALL_DEADLINE: durationDays,
            SimProject.KEY_TIME_ELAPSED: timeElapsed,
            SimProject.KEY_BUDGET_ELAPSED: budgetElapsed,
            SimProject.KEY_CODE_COMMITS: numCommits,
            SimProject.KEY_CODE_BUGS_RESOLUTION: defectFixRate,
            SimProject.KEY_SUBDEADLINES_MET_PROPORTION: proportionSubdeadlinesMet,
            SimProject.KEY_TEAM_AVG_RANK: avgTeamRank,
            SimProject.KEY_TEAM_SIZE: teamSize,
            SimProject.KEY_MET_COMMUNICATION: teamCommunication,
            SimProject.KEY_MET_MORALE: teamMorale,
            SimProject.KEY_MET_COMMITMENT: teamCommitment,
            SimProject.KEY_MET_SUPPORT: teamSupport,
            SimProject.KEY_MET_PLANNING: projectPlanning
        }

        return pd.Series(projectStateDict)
    
        # Append the given state to the Model's training data in CSV format
    def write_state_to_training_data(self, state):
        targetFile = open(CSV_TRAINING_DATA, "a")
        targetFile.write(state.to_csv(lineterminator='\n', header=False))
        targetFile.close()



    # Given a completed project, evaluate its success and write that project to the end of the 
    # Risk-Assessment-Model training data
    def add_project_to_training_data(self, projectID):
        STATUS_FINISHED = 1
        STATUS_CANCELLED = 2 
        status = Hard_Metrics.query(Hard_Metrics.status).filter_by(projectID = projectID).first()

        # If project finished, mark as success
        if status == STATUS_FINISHED:
            succReport = SuccessReport()
            finalSurveyResponse = End_Result.query.filter_by(projectID = projectID).first()

            if finalSurveyResponse != None:
                finance = finalSurveyResponse.financeMetric
                code = finalSurveyResponse.codeMetric
                timescale = finalSurveyResponse.timescaleMetric
                management = finalSurveyResponse.managementMetric
                team = finalSurveyResponse.teamMetric
                succReport.set_success_values(finance, timescale, team, code, management)

                projectState = self.get_project_state()
                succReport.add_binary_to_state(projectState)

                self.write_state_to_training_data(projectState)
        # If project cancelled, mark as failure
        elif status == STATUS_CANCELLED:
            succReport = SuccessReport()
            projectState = self.get_project_state()
            succReport.add_binary_to_state(projectState)

            self.write_state_to_training_data(projectState)


    def retrain_model(self):
        train_all_models()

