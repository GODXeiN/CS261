# Arbitrarily selected. To be reviewed
criticalBud = 0.3
riskyBud = 0.5
criticalTime = 0.3
riskyTime = 0.5
criticalCode = 0.3
riskyCode = 0.5
criticalTeam = 0.3
riskyTeam = 0.5
criticalMan = 0.3
riskyMan = 0.5

class suggSys():
    def __init__(self,budgetRisk,timeRisk,codeRisk,teamRisk,managementRisk):
        self.budgetRisk = budgetRisk
        self.timeRisk = timeRisk
        self.codeRisk = codeRisk
        self.teamRisk = teamRisk
        self.managementRisk = managementRisk
    
    def getBudgetRisk(self):
        if self.budgetRisk < criticalBud:
            return "The budget is far below the requirements of the project. It is strongly recommended to increase the funding or reduce the team size in order to succeed."
        elif self.budgetRisk < riskyBud:
            return "The budget may not be sufficient for the whole duration of the project. It is recommended to increase the funding or reduce the team size for greater chance of success."
        else:
            return "The budget is likely sufficient for the project. For the highest chance of success, ensure your project has a contingency fund, in case of unexpected development costs."
    
    def getTimeRisk(self):
        if self.timeRisk < criticalTime:
            return "The project is not on-track and has a high likelihood of not meeting the final deadline. It is strongly recommended to postpone the deadline and increase the team size."
        elif self.timeRisk < riskyTime:
            return "The project is at risk of not meeting its deadlines. It is recommended to postpone the deadline or increase the team size."
        else:
            return "The project is on-track to meet its deadlines. You should avoid moving the deadline closer or altering the requirements during development."
        
    def getCodeRisk(self):
        if self.codeRisk < criticalCode:
            return "The project repository is likely to contain many unresolved bugs and critically low levels of commits compared to previous months. It is strongly recommended to check-in with all members of the development team. Consider postponing the deadline or introducing more team members."
        elif self.codeRisk < riskyCode:
            return "The project repository may contain unresolved bugs or some members of the development team may be behind on code commits. It is recommended to check-in with all members of the development team and if any issues arise, introduce more team members."
        else:
            return "The project repository is being regularly updated and outstanding issues are being resolved. Continue to monitor this aspect as the project approaches completion." 
    
    def getTeamRisk(self):
        if self.teamRisk < criticalTeam:
            return "The project team is showing high levels of fatigue and failure. You should address this issue immediately - consider reducing team-member work-loads, introducing more team members, and prioritising team morale."
        elif self.teamRisk < riskyTeam:
            return "The project team is showing some signs of fatigue and failure. You may wish to consider reducing team-member work-loads or showing departmental support for the project."
        else:
            return "The project team is operating well and has a good chance of succeeding. To prevent future issues, ensure that the team is not over-worked and communicates well."
    
    def getManagementRisk(self):
        if self.managementRisk < criticalMan:
            return "The management of the team is likely to fail. It is strongly recommended that management increases its support for the project and the team."
        elif self.managementRisk < riskyMan:
            return "The management of the team has a moderate risk of failure. It is recommended that the top management shows their commitment to the success of the project, for example, by having one-on-one sessions with team members to understand any issues they are facing."
        else:
            return "The management of the team is likely to succeed. Continue to provide the team with support and show your commitment to the project."
           
