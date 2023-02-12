import pandas as pd
import numpy as np

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from projectDf import independent_headers

# The file to which the trained model will be saved
MODEL_SAVE_DEST = 'logregmodelpipeline.joblib'

# Open the project training/test data
df = pd.read_csv("testDataStaged.csv")

# Dependent field; the field we want to model to predict
target_attr = 'Success'

# Get the independent data as a matrix
x = np.array(df[independent_headers])
y = np.array(df[target_attr])

# Sequence a scaler and the model, so any input data is normalised before being fed to the model
pipeLR = Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])

# Split the imported data into training and test components
# Stratify ensures that the proportion of each class is maintained
# e.g. if the data contains 25% success, then training contains 25% success and test data contains 25% success
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1, stratify=y)

# TRAINING using training dataset
pipeLR.fit(X_train, y_train)

# PREDICTION using test dataset
y_pred = pipeLR.predict(X_test)

# Evaluate the model's accuracy by comparing the prediction to the actual test y-values
print(classification_report(y_test, y_pred))

# Export the trained model pipeline
from joblib import dump
dump(pipeLR, MODEL_SAVE_DEST) 