from . import models as DB

from random import Random
import pandas as pd
import projectRiskInterface as PRI
import RiskAssessment as RA

# TODO - change this 
MANAGER_ID = 1

budget = 100000
deadline = 91
projectID = 10001

startDate = "01/01/2023"
startDT = pd.to_datetime(startDate)
startTS = int(startDT)
endDate = startDT + pd.Timedelta(days=deadline)
print(str(endDate))

DB.Project.add(projectID=projectID, managerID=MANAGER_ID, dateCreated=startTS, title="Messager", dateLastSurveyed=startTS, dateLastRiskCalculation=startTS, updateInterval=7)

rand = Random()

currDay = 0
deadlineID = 20000

# 1 = met, 2 = unmet, 0 = ongoing
deadlines = [("2023/01/21", "Requirements", 1),
             ("2023/02/01", "Design & Prototyping", 2),
             ("2023/02/19", "Implement Database", 1),
             ("2023/03/01", "Implement Login System", 1),
             ("2023/03/17", "Implement Messaging", 0),
             ("2023/04/01", "Implement Navigation", 0)]

for dl in deadlines:
    dt = pd.to_datetime(dl[0])
    ts = int(dt.timestamp())
    title = dl[1]
    status = dl[2]
    DB.Deadline.add(deadlineID=deadlineID, projectID=projectID, title=title, deadlineDate=ts, achieved=status)
    print("Added deadline", str((deadlineID, projectID, title, ts, status)))
    deadlineID += 1


#projectID = db.Column(db.Integer, db.ForeignKey('Project.projectID'), primary_key = True)
# date = db.Column(db.Integer, primary_key = True)
# budget = db.Column(db.Integer)
# costToDate = db.Column(db.Integer)
# deadline = db.Column(db.Integer)
# status = db.Column(db.Integer)#0ong,1fin,2

# budget, cost, date, deadline, status
hm_rows = [(100000,  200, "2023/01/07", endDate, 0),
           (100000, 4490, "2023/01/14", endDate, 0),
           (100000, 7720, "2023/01/21", endDate, 0),
           (100000,11000, "2023/01/28", endDate, 0),
           (100000,14200, "2023/02/04", endDate, 0),
           (100000,21500, "2023/02/11", endDate, 0),
           (100000,29150, "2023/02/18", endDate, 0),
           (100000,43870, "2023/02/25", endDate, 0),
           (100000,51400, "2023/03/04", endDate, 0)
        ]

pri = PRI.ProjectRiskInterface()

for (bdgt, cost, day, deadline, status) in hm_rows:
    dt = pd.to_datetime(day)
    ts = int(dt.timestamp())
    dl_ts = int(deadline.timestamp())

    DB.Hard_Metrics.add(projectID=projectID, date=ts, budget=bdgt, costToDate=cost, deadline=dl_ts, status=status)

    # Get a new risk assessment after each weekly update
    riskAssessment = pri.get_risk_assessment(projectID)

    overallRisk = riskAssessment.get_success_attribute(RA.KEY_OVERALL)
    financeRisk = riskAssessment.get_success_attribute(RA.KEY_FINANCE)
    managementRisk = riskAssessment.get_success_attribute(RA.KEY_MANAGEMENT)
    codeRisk = riskAssessment.get_success_attribute(RA.KEY_CODE)
    teamRisk = riskAssessment.get_success_attribute(RA.KEY_TEAM)
    timescaleRisk = riskAssessment.get_success_attribute(RA.KEY_TIMESCALE)

    DB.Risk.add(projectID=projectID, date=ts, riskLevel=overallRisk, riskFinance=financeRisk, riskManagement=managementRisk, riskCode=codeRisk, riskTeam=teamRisk, riskTimescale=timescaleRisk)
    print("Added HardMetric", str((projectID, ts, bdgt, cost, dl_ts, status)))
    print("Got RiskAssessment:", str(riskAssessment))

