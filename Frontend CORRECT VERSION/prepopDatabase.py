from . import models as DB
from . import db
from random import Random
import pandas as pd
from .projectRiskInterface import ProjectRiskInterface as PRI
from .model.RiskAssessment import RiskAssessment as RA
import time
import sys
# TODO - change this 

class prepop():
    def __init__(self,mID):
        self.mID = mID
    def populate(self):
        MANAGER_ID = self.mID
        budget = 100000
        deadline = 91
        startDate = "01/01/2023"
        startDT = pd.to_datetime(startDate)
        startTS = time.mktime(startDT.timetuple())
        endDate = startDT + pd.Timedelta(days=deadline)
        print(startTS,file=sys.stderr)

        
        project = DB.Project(managerID=MANAGER_ID, dateCreated=startTS, title="Messager", dateLastSurveyed=startTS, dateLastRiskCalculation=startTS, updateInterval=7)
        
        db.session.add(project)
        db.session.commit()
        projectID = DB.Project.query.filter_by(managerID=MANAGER_ID, title="Messager").first().projectID
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

            dead = DB.Deadline(projectID=projectID, title=title, deadlineDate=ts, achieved=status)
            db.session.add(dead)
            db.session.commit()
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

        

        for (bdgt, cost, day, deadline, status) in hm_rows:
            dt = pd.to_datetime(day)
            ts = int(dt.timestamp())
            dl_ts = int(deadline.timestamp())
            print(ts,file=sys.stderr)
            hard = DB.Hard_Metrics(projectID=projectID, date=ts, budget=bdgt, costToDate=cost, deadline=dl_ts, status=status)
            db.session.add(hard)
            db.session.commit()
            # Get a new risk assessment after each weekly update
            pri = PRI()
            riskAssessment = pri.get_risk_assessment(projectID)
            KEY_FINANCE = 'Finance'
            KEY_TEAM = 'Team'
            KEY_TIMESCALE = 'Timescale'
            KEY_MANAGEMENT = 'Management'
            KEY_CODE = 'Code'
            KEY_OVERALL = 'Overall'
            overallRisk = riskAssessment.get_success_attribute(KEY_OVERALL)
            financeRisk = riskAssessment.get_success_attribute(KEY_FINANCE)
            managementRisk = riskAssessment.get_success_attribute(KEY_MANAGEMENT)
            codeRisk = riskAssessment.get_success_attribute(KEY_CODE)
            teamRisk = riskAssessment.get_success_attribute(KEY_TEAM)
            timescaleRisk = riskAssessment.get_success_attribute(KEY_TIMESCALE)

            risk = DB.Risk(projectID=projectID, date=ts, riskLevel=overallRisk, riskFinance=financeRisk, riskManagement=managementRisk, riskCode=codeRisk, riskTeam=teamRisk, riskTimescale=timescaleRisk)
            db.session.add(risk)
            db.session.commit()
            print("Added HardMetric", str((projectID, ts, bdgt, cost, dl_ts, status)))
            print("Got RiskAssessment:", str(riskAssessment))


