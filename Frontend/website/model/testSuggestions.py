from suggestionSys import suggSys
import projectDf as Project
import RiskAssessment
from RiskAssessmentGenerator import RiskAssessmentGenerator as RAG

project = Project.SimProject(1,500000,500000,1,100,200)
project.simulate()
print(str(project))

sampleRows = project.statesDf.sample(1)
sampleRow = sampleRows.iloc[0]
print(sampleRow)

rag = RAG()
ra = rag.generate_ra(sampleRow)

print(str(ra))

budgetRisk = ra.get_success_attribute(RiskAssessment.KEY_FINANCE)
codeRisk = ra.get_success_attribute(RiskAssessment.KEY_CODE)
timeRisk = ra.get_success_attribute(RiskAssessment.KEY_TIMESCALE)
managementRisk = ra.get_success_attribute(RiskAssessment.KEY_MANAGEMENT)
teamRisk = ra.get_success_attribute(RiskAssessment.KEY_TEAM)



suggProv = suggSys(budgetRisk, timeRisk, codeRisk, teamRisk, managementRisk)
print("\n ----- SUGGESTIONS ----- ")
print(" *", suggProv.getBudgetRisk())
print(" *", suggProv.getCodeRisk())
print(" *", suggProv.getTimeRisk())
print(" *", suggProv.getTeamRisk())
print(" *", suggProv.getManagementRisk())