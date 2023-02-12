from joblib import load
from projectDf import independent_headers
from logregStaged import MODEL_SAVE_DEST


# Reload the model from the saved dump
pipeLR = load(MODEL_SAVE_DEST)

# Manual Test (Can be removed)
# Creates a project, finds its success then gets the model to predict.

print("Manually Testing Model...")

from projectDf import Project

p = Project(10000,10,11,100000,500,2000)
p.simulate()

# Get a single sample from the project and transpose it
pSample = p.get_labelled_samples(1).iloc[0].T

# Extract the headers for the prediction, then convert the project to an array, 
# Then reshape to a matrix containing a single data-point vector
proj_x = pSample[independent_headers].to_numpy().reshape(1,-1)
print("My Project: ")
print(str(pSample))

# Get the prediction 
# (note: this is normalised, so if the output is not 0/1, we need to de-normalise it)
p_pred = pipeLR.predict(proj_x)

# Display prediction
if p_pred[0] == 1:
    print(" >>> LogReg prediction: Success (1)")
elif p_pred[0] == -1:
    print(" >>> LogReg prediction: Cancelled (-1)")
else:
    print(" >>> LogReg prediction: Failure (0)")
