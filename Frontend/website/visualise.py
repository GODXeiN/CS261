import  matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response, Risk
import time

slices = 10

class visualise():
    def __init__(self, pID):
        self.pID = pID
    def overallRisk(self):
        risks = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc())
        riskLast = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.desc()).first()
        riskFirst = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc()).first()
        timescale = riskLast.date - riskFirst.date
        timeperiod = timescale/slices
        riskSlice = []
        x = []
        yMax = []
        yMin = []
        totalTime = riskFirst.date
        for i in range(0,slices):
            x.append(totalTime)
            totalTime += timeperiod
        for risk in risks:
            if risk.date < riskFirst.date + timescale:
                riskSlice.append(risk.riskLevel)
            else:
                timescale += timeperiod
                if len(riskSlice) > 0:
                    yMax.append(max(riskSlice))
                    yMin.append(min(riskSlice))
        fig, ax = plt.subplots()
        if len(yMax) < slices:
            for i in range(0,slices - len(yMax)):
                yMax.append(0)
        if len(yMin) < slices:
            for i in range(0,slices - len(yMin)):
                yMin.append(0)
        ax.plot(x, yMax)
        ax.plot(x, yMin)

        #plt.show()   
        plt.savefig(os.path.join(os.getcwd(),'website','static','risk.png'))
        plt.close(fig)

    def budget(self):
        metrics = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.asc())
        metLast = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.desc()).first()
        metFirst = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.asc()).first()
        timescale = metLast.date - metFirst.date
        timeperiod = timescale/slices
        costSlice = []
        budgetSlice = []
        x = []
        yCost = []
        yBudget = []
        totalTime = metFirst.date
        for i in range(0,slices):
            x.append(totalTime)
            totalTime += timeperiod
        for metric in metrics:
            if metric.date < metFirst.date + timescale:
                costSlice.append(metric.costToDate)
                budgetSlice.append(metric.budget)
            else:
                timescale += timeperiod
                if len(costSlice) > 0:
                    yCost.append(max(costSlice))
                if len(budgetSlice) > 0:
                    yBudget.append(min(budgetSlice))
        fig, ax = plt.subplots()
        if len(yCost) < slices:
            for i in range(0,slices - len(yCost)):
                yCost.append(0)
                yBudget.append(0)
        ax.plot(x, yBudget)
        ax.plot(x,yCost)
        #plt.show()   
        plt.savefig(os.path.join(os.getcwd(),'website','static','budget.png'))
        plt.close(fig)

    # def timeline(self):
    #     #time.time() may not be unix time
    #     deadlines = Deadline.query.filter_by(projectID = self.pID).filter_by(Deadline.deadlineDate > int(time.time())).order_by(Deadline.deadlineDate.asc())
    #     lastDeadline = Deadline.query.filter_by(projectID = self.pID).filter_by(Deadline.deadlineDate > int(time.time())).order_by(Deadline.deadlineDate.desc()).first()
    #     x = [int(time.time())]
    #     y = []
    #     for deadline in deadlines:
    #         if not deadline.achieved:
    #             x.append()

 