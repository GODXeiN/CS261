import  matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response, Risk
import time
import datetime
import sys

from matplotlib.ticker import ScalarFormatter

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
            x.append(datetime.datetime.fromtimestamp(totalTime))
            totalTime += timeperiod
        totalTime = riskFirst.date
        
        for risk in risks:
            print(risk.riskLevel,file=sys.stderr)
            riskSlice.append(risk.riskLevel)
            if risk.date < totalTime + timeperiod:
                print("risk")
            else:
                totalTime += timeperiod
                if len(riskSlice) > 0:
                    yMax.append(max(riskSlice))
                    yMin.append(min(riskSlice))
                riskSlice = []
        fig, ax = plt.subplots()
        if len(yMax) < slices:
            for i in range(0,slices - len(yMax)):
                yMax.append(0)
        if len(yMin) < slices:
            for i in range(0,slices - len(yMin)):
                yMin.append(0)
        ax.plot(x, yMax, color='red',label='Max risk')
        ax.plot(x, yMin, color='blue',label='Min risk')
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        #plt.ticklabel_format(axis='y',useOffest=False,style='plain') 
        plt.xticks(rotation=90)
        #plt.show()   
        
        plt.title("Risk analysis")
        plt.xlabel('Date')
        plt.ylabel('Risk level')
        plt.tight_layout()
        plt.legend(loc="upper left")
        plt.savefig(os.path.join(os.getcwd(),'Frontend 3-8-2023','website','static','risk.png'))
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
        totalTime = metFirst.date + timeperiod
        for i in range(0,slices):
            x.append(datetime.datetime.fromtimestamp(totalTime))
            totalTime += timeperiod
        totalTime = metFirst.date
        for metric in metrics:
            print(metric.costToDate, file=sys.stderr)
            print(metric.date, file=sys.stderr)
            print(totalTime, file=sys.stderr)
            costSlice.append(metric.costToDate)
            budgetSlice.append(metric.budget)
            if metric.date < totalTime:
                print("metric",file=sys.stderr)
                
            else:
                totalTime += timeperiod
                if len(costSlice) > 0:
                    yCost.append(max(costSlice))
                if len(budgetSlice) > 0:
                    yBudget.append(max(budgetSlice))
                costSlice = []
                budgetSlice = []
        fig, ax = plt.subplots()
        if len(yCost) < slices:
            for i in range(0,slices - len(yCost)):
                yCost.append(yCost[-1])
                yBudget.append(yBudget[-1])
        ax.plot(x, yBudget, color='blue',label='budget')
        ax.plot(x,yCost, color='red',label='cost')
        plt.xticks(rotation=90)
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        #Removes scienitifc notation
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        #plt.ticklabel_format(useOffset=False)
        plt.title("Budget analysis")
        plt.xlabel('Date')
        plt.ylabel('Budget')
        plt.legend(loc="upper left")
        #plt.show()   
        plt.tight_layout()
        plt.savefig(os.path.join(os.getcwd(),'Frontend 3-8-2023','website','static','budget.png'))
        plt.close(fig)
