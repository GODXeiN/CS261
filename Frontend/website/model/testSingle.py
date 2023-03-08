## Tests the Logistic Regression Model with a single project 


from joblib import load
from projectDf import SimProject, independent_headers

import RiskAssessmentGenerator 

rag = RiskAssessmentGenerator.RiskAssessmentGenerator()

print("Single Testing Model\n")

# Creates an arbitrary project
p = SimProject(10001, 10, 30, 10000, 200, 500)
p.simulate()
successRep = p.evaluate()
print(str(successRep))

# Get a single sample from the project
pSample = p.get_labelled_samples(1).iloc[0]

# print("Artificial Project: ")
# print(str(pSample))

# Generate the Risk-Assessment and display it
ra = rag.generate_ra(pSample)
print(ra)
