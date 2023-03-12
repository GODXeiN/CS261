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

#Alter for more precision
slices = 7

class visualise():
    def __init__(self, pID):
        self.pID = pID
    def overallRisk(self):
        risks = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc())
        riskLast = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.desc()).first()
        riskFirst = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc()).first()
        timescale = riskLast.date - riskFirst.date
        #Only one assessment
        if timescale == 0:
            riskLast = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.desc()).first()
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
        for i in range(0,slices):
            for risk in risks:
                print(risk.riskLevel,file=sys.stderr)
                if totalTime <= risk.date and risk.date < totalTime + timeperiod:
                    riskSlice.append(risk.riskLevel)
            if len(riskSlice) > 0:
                yMax.append(max(riskSlice))
                yMin.append(min(riskSlice))
            elif totalTime == riskFirst.date:
                yMax.append(0)
                yMin.append(0)
            else:
                yMax.append(yMax[-1])
                yMin.append(yMin[-1])
                
            riskSlice = []
            totalTime += timeperiod
        fig, ax = plt.subplots()
        ax.plot(x, yMax, color='red',label='Highest success rate')
        ax.plot(x, yMin, color='blue',label='Lowest success rate')
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        #plt.ticklabel_format(axis='y',useOffest=False,style='plain') 
        plt.xticks(rotation=90)
        #plt.show()   
        
        plt.title("Success analysis")
        plt.xlabel('Date')
        plt.ylabel('Success level')
        plt.tight_layout()
        plt.legend(loc="upper left")
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
        totalTime = metFirst.date + timeperiod
        for i in range(0,slices):
            x.append(datetime.datetime.fromtimestamp(totalTime))
            totalTime += timeperiod
        totalTime = metFirst.date
        for i in range(0,slices):
            for metric in metrics:
                print(metric.costToDate, file=sys.stderr)
                print(metric.date, file=sys.stderr)
                print(totalTime, file=sys.stderr)
                if totalTime <= metric.date and metric.date < totalTime + timeperiod:
                    costSlice.append(metric.costToDate)
                    budgetSlice.append(metric.budget)
            
            if len(costSlice) > 0:
                yCost.append(max(costSlice))
                yBudget.append(max(budgetSlice))
            elif totalTime == metFirst.date:
                yCost.append(0)
                yBudget.append(0)
            else:
                yCost.append(yCost[-1])
                yBudget.append(yBudget[-1])
            
                    
            totalTime += timeperiod
            costSlice = []
            budgetSlice = []
        fig, ax = plt.subplots()
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
        plt.savefig(os.path.join(os.getcwd(),'website','static','budget.png'))
        plt.close(fig)

 
