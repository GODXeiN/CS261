## Tests the Logistic Regression Model with a single project 


from joblib import load
import pandas as pd
import numpy as np
from projectDf import independent_headers
from sklearn.metrics import classification_report

from logregTrainer import OVERALL_MODEL_SAVE_DEST
from projectDf import independent_headers


# Reload the model from the saved dump
pipeLR = load(OVERALL_MODEL_SAVE_DEST[0])

# Manual Test (Can be removed)
# Creates a project, finds its success then gets the model to predict.

print("Bulk Testing Model...")

df = pd.read_csv("./data/testDataStaged.csv")

# Dependent field; the field we want to model to predict
target_attr = 'Success'

# Get the independent data as a matrix
x = np.array(df[independent_headers])
y = np.array(df[target_attr])


y_pred = pipeLR.predict(x)

print(classification_report(y, y_pred))


# Get the model accuracy and write it to a file
result = pipeLR.score(x, y)
print("Overall accuracy:", str(result))
