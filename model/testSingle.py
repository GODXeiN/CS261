## Tests the Logistic Regression Model with a single project 


from joblib import load
from projectDf import SimProject, independent_headers

import RiskAssessmentGenerator 

rag = RiskAssessmentGenerator.RiskAssessmentGenerator()

print("Single Testing Model\n")

# Creates an arbitrary project
p = SimProject(10001, 4, 30, 10000, 200, 1000)
p.simulate()
successRep = p.evaluate()
print(str(successRep))

# Get a single sample from the project
pSample = p.get_labelled_samples(1).iloc[0]

# Convert the data point from a row to a vector for input into the models
proj_x = pSample[independent_headers].to_numpy().reshape(1,-1)

# print("Artificial Project: ")
# print(str(pSample))

# Generate the Risk-Assessment and display it
ra = rag.generate_ra(proj_x)
print(ra)


#### Old approach for a single model

# Get the prediction 
# p_pred = pipeLR.predict(proj_x)

# # Get the confidence of the model in each outcome ([0] = failure, [1] = success)
# confProbs = pipeLR.predict_proba(proj_x)[0]
# print("\nConfidence Probabilities:", str(confProbs))

# # Load the saved accuracy of the model, so we can determine the likelihood of its prediction being accurate
# accuracyFile = open(OVERALL_MODEL_ACCURACY_DEST, 'r')
# mdlAccuracy = float(accuracyFile.read())
# accuracyFile.close()

# # Display result of prediction
# if p_pred[0] == 1:
#     print(" >>> LogReg prediction: (1-Success)")
#     print(" >>> Model Confidence:", confProbs[1])
# elif p_pred[0] == 0:
#     print(" >>> LogReg prediction: (0-Failure)")
#     print(" >>> Model Confidence:", confProbs[0])
# else:
#     print(" >>> LogReg prediction: Cancelled (-1)")

# # Determine the overall chance of success by using Conditional Probability & Bayes Formula
# # SUCCESS = MODEL_SUCCESS * MODEL_ACCURATE + (1-MODEL_FAILURE) * MODEL_INACCURATE
# overallSuccessEst = confProbs[1] * mdlAccuracy + confProbs[0] * (1-mdlAccuracy)
# # Convert estimation to a probability
# overallSuccessProb = round(100 * overallSuccessEst, 2)

# print("\nOverall Estimation of Success:", str(overallSuccessProb) + "%")