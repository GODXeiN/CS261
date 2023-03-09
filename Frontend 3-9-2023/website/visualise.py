import matplotlib.pyplot as plt
from .models import Project, Git_Link, Hard_Metrics, Worker, Deadline, Works_On, End_Result, Survey_Response, Risk


class visualise():
    def __init__(self, pID):
        self.pID = pID
    def overallRisk(self):
        risks = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc())
        riskLast = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.desc()).first()
        riskFirst = Risk.query.filter_by(projectID = self.pID).order_by(Risk.date.asc()).first()
        timescale = riskLast - riskFirst
        timeperiod = timescale/10
        riskSlice = []
        x = []
        yMax = []
        yMin = []
        totalTime = riskFirst
        for i in range(0,10):
            x.append(totalTime)
            totalTime += timeperiod
        for risk in risks:
            if risk.date < riskFirst + timescale:
                riskSlice.append(risk.riskLevel)
            else:
                timescale += timeperiod
                yMax.append(max(riskSlice))
                yMin.append(min(riskSlice))
        fig, ax = plt.subplots()
        ax.plot(x, yMax)
        ax.plot(x,yMin)

        #plt.show()   
        plt.savefig('risk.png')

    def budget(self):
        metrics = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.asc())
        metLast = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.desc()).first()
        metFirst = Hard_Metrics.query.filter_by(projectID = self.pID).order_by(Hard_Metrics.date.asc()).first()
        timescale = metLast - metFirst
        timeperiod = timescale/10
        costSlice = []
        budgetSlice = []
        x = []
        yCost = []
        yBudget = []
        totalTime = metFirst
        for i in range(0,10):
            x.append(totalTime)
            totalTime += timeperiod
        for metric in metrics:
            if metric.date < metFirst + timescale:
                costSlice.append(metric.costToDate)
                budgetSlice.append(metric.budgetSlice)
            else:
                timescale += timeperiod
                yCost.append(max(costSlice))
                yBudget.append(min(budgetSlice))
        fig, ax = plt.subplots()
        ax.plot(x, yBudget)
        ax.plot(x,yCost)
        #plt.show()   
        plt.savefig('static/budget.png')

    # def timeline(self):
    #     #time.time() may not be unix time
    #     deadlines = Deadline.query.filter_by(projectID = self.pID).filter_by(Deadline.deadlineDate > int(time.time())).order_by(Deadline.deadlineDate.asc())
    #     lastDeadline = Deadline.query.filter_by(projectID = self.pID).filter_by(Deadline.deadlineDate > int(time.time())).order_by(Deadline.deadlineDate.desc()).first()
    #     x = [int(time.time())]
    #     y = []
    #     for deadline in deadlines:
    #         if not deadline.achieved:
    #             x.append()

 