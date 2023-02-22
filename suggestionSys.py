critical = 0.3
risky = 0.6
addressable = 1
class suggSys():
    def __init__(self,budgetRisk,timeRisk,codeRisk,teamRisk,managementRisk):
        self.budgetRisk = budgetRisk
        self.timeRisk = timeRisk
        self.codeRisk = codeRisk
        self.teamRisk = teamRisk
        self.managementRisk = managementRisk
    
    def getBudgetRisk(self):
        if self.budgetRisk < critical:
            return "The budget is not enough to meet all the needs of the project. It is strongly recommended to increase the funding or reduce the team size in order to succeed."
        elif self.budgetRisk < risky:
            return "The budget might not be enough for the whole duration of the project. It is recommended to increase the funding or reduce the team size in order to succeed."
        else:
            return "The budget could eventually not be enough. You could consider increasing the funding or reducing the team size."
    
    def getTimeRisk(self):
        if self.timeRisk < critical:
            return "The project is not on track and will most likely not meet the final deadline. It is strongly recommended to change the requirements or push the deadline."
        elif self.timeRisk < risky:
            return "The project has missed some internal deadlines throughout the length of development. It is recommended to change the requirements or push the deadline."
        else:
            return "The project has missed only a few internal deadlines. You could consider changing the requirements or the deadline in order to succeed."
        
    def getCodeRisk(self):
        if self.codeRisk < critical:
            return "The code has a lot of unresolved bugs and critically low levels of  commits compared to previous months. These issues must be addressed. It is strongly recommended to check on the software development team regarding their progress and what issues they may be facing in regards to the code."
        elif self.codeRisk < risky:
            return "The code has unresolved bugs and much less commits compared to previous months. These issues should be addressed. It is recommended to check on the software development team regarding their progress and what issues they may be facing in regards to the code."
        else:
            return "The code may have some unresolved bugs and less commits compared to previous months. Consider checking on the software development team regarding their progress and what issues they may be facing in regards to the code." 
    def getTeamRisk(self):
        if self.teamRisk < critical:
            return "Team aspect of project is at a critical level and must be addressed immediately, this may be due to several aspects such as: low team communication, low team commitment, low team morale."
        elif self.teamRisk < risky:
            return "Team aspect of project is at a risky level and should be addressed, this may be due to several aspects such as: low team communication, low team commitment, low team morale."
        else:
            return "Team aspect of project is may not be at a satisfactory level, this may be due to several aspects such as: low team communication, low team commitment, low team morale."
    def getManagementRisk(self):
        if self.managementRisk < critical:
            return "Members of the team feel extremely neglected by the top-level management. It is strongly recommended that the top management shows their commitment to the success of the project through things such as having one-on-one sessions with the team members to get to know how they’re feeling regarding the project and any issues they may have."
        elif self.managementRisk < risky:
            return "Members of the team don’t feel supported by the top-level management. It is recommended that the top management shows their commitment to the success of the project through things such as having one-on-one sessions with the team members to get to know how they’re feeling regarding the project and any issues they may have."
        else:
            return "Members of the team may feel slightly unsupported by the top-level management. Consider getting the top management to show their commitment to the success of the project through things such as having one-on-one sessions with the team members to get to know how they’re feeling regarding the project and any issues they may have."
        

def main():
    suggs = suggSys(0.9,0.5,0.1,0.2,1)
    print(suggs.getBudgetRisk())
    print(suggs.getTimeRisk())
    print(suggs.getCodeRisk())
    print(suggs.getTeamRisk())
    print(suggs.getManagementRisk())
    
main()
   
