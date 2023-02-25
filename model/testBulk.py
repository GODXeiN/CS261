## Tests the Logistic Regression Model with a single project 


from joblib import load
import pandas as pd
import numpy as np
from projectDf import independent_headers
from sklearn.metrics import classification_report
from logregTrainer import OVERALL_MODEL_SAVE_DEST, FINANCE_MODEL_SAVE_DEST, TIMESCALE_MODEL_SAVE_DEST, CODE_MODEL_SAVE_DEST, MANAGEMENT_MODEL_SAVE_DEST, TEAM_MODEL_SAVE_DEST


# Reload the model from the saved dump
pipeLR = load(OVERALL_MODEL_SAVE_DEST[0])

# Manual Test (Can be removed)
# Creates a project, finds its success then gets the model to predict.

print("Bulk Testing Model...")

df = pd.read_csv("./data/testDataStaged.csv")


# Get the independent data as a matrix
x = np.array(df[independent_headers])
# Dependent field; the field we want to model to predict
y = np.array(df['Success'])


y_pred = pipeLR.predict(x)

modelTests = [
    (FINANCE_MODEL_SAVE_DEST[0], 'Finance Success'),
    (TIMESCALE_MODEL_SAVE_DEST[0], 'Timescale Success'),
    (CODE_MODEL_SAVE_DEST[0], 'Code Success'),
    (MANAGEMENT_MODEL_SAVE_DEST[0], 'Management Success'),
    (TEAM_MODEL_SAVE_DEST[0], 'Team Success')
]

for (saveFile, targetAttr) in modelTests:
    model = load(saveFile)
    y_test = np.array(df[targetAttr])
    score = model.score(x, y_test)
    print(" *", str(targetAttr), "accuracy:", str(score))

print("Overall Performance:")
print(classification_report(y, y_pred))

# Get the model accuracy and write it to a file
result = pipeLR.score(x, y)
print("Overall accuracy:", str(result))
