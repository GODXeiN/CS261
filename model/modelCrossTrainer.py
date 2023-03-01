import pandas as pd
import numpy as np
from os.path import isdir
from os import makedirs

from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold

from projectDf import independent_headers, KEY_ID
from joblib import dump
from logregTrainer import TRAINED_MODEL_DIR, OVERALL_MODEL_SAVE_DEST, FINANCE_MODEL_SAVE_DEST, TIMESCALE_MODEL_SAVE_DEST, CODE_MODEL_SAVE_DEST, MANAGEMENT_MODEL_SAVE_DEST, TEAM_MODEL_SAVE_DEST

csvdata = "./data/trainDataStaged.csv"

# Open the project training/test data
df = pd.read_csv(csvdata)
print("Loaded Training File:", csvdata)

# Dependent field; the field we want to model to predict
target_attr = 'Success'


# If the model target directory is not present, make it
if not isdir(TRAINED_MODEL_DIR):
    makedirs(TRAINED_MODEL_DIR)


# Get the project ID from each row, so we can ensure that data from the 
# same project does not appear in both training and test splits
projectGroups = np.array(df[KEY_ID])

# Cross-Validation K-Fold Generator
gkf = GroupKFold(n_splits=5)


# Creates a Pipeline model (with data standardisation) and trains it with CrossValidation to 
# recognise the columns given by independent_headers and predict the column 'dependent_header'. 
# Then, exports the trained model and its accuracy score to the given destination files.
def train_model_and_dump(independent_headers, dependent_header, model_save_dest, model_accuracy_dest):
    # Get the independent data as a matrix
    x = np.array(df[independent_headers])
    y = np.array(df[dependent_header])

    # Store the trained model with the most accurate performance
    bestEstimator = None
    bestScore = 0
    
    # Train the model on each data split, retaining the configuration with the most accuracy
    # Note: train and test are arrays of indexes, not the data itself
    for train, test in gkf.split(x, y, groups=projectGroups):
        # Sequence a scaler and the model, so any input data is normalised before being fed to the model
        pipeLR = Pipeline([('scaler', StandardScaler()), ('sgd', SGDClassifier())])

        # Get the data using the indexes produced by GroupKFold
        x_train = x[train]
        y_train = y[train]
        x_test = x[test]
        y_test = y[test]

        # Train the model on the training split
        pipeLR.fit(x_train, y_train)
        # Then get predictions for the test split
        y_pred = pipeLR.predict(x_test)

        # Measure the regression error of the model (difference from true)
        mse = mean_squared_error(y_test, y_pred)
        print(" > MSE:",str(mse))

        # Get the model's accuracy (note: accuracy + mse = 1)
        modelScore = accuracy_score(y_test, y_pred)

        # Only retain the model which exhibits the highest score (most accurate)
        if modelScore > bestScore:
            bestEstimator = pipeLR
            bestScore = modelScore

    print("Best Score:", str(bestScore))

    y_pred = bestEstimator.predict(x)
    print(classification_report(y, y_pred))

    # Save the accuracy of the model 
    # (so the Risk-Assessment has the likelihood the model is correct)
    accuracyFile = open(model_accuracy_dest, "w")
    accuracyFile.write(str(bestScore))
    accuracyFile.close() 

    # # Export the trained model for use by the Risk-Assessment system
    dump(bestEstimator, model_save_dest)


# Each tuple describes one model to be trained
modelParams = [
    (independent_headers, 'Success', OVERALL_MODEL_SAVE_DEST),
    (independent_headers, 'Finance Success', FINANCE_MODEL_SAVE_DEST),
    (independent_headers, 'Timescale Success', TIMESCALE_MODEL_SAVE_DEST),
    (independent_headers, 'Code Success', CODE_MODEL_SAVE_DEST),
    (independent_headers, 'Team Success', TEAM_MODEL_SAVE_DEST),
    (independent_headers, 'Management Success', MANAGEMENT_MODEL_SAVE_DEST)
]


# Train a model for each of the identified target parameters, 
# dumping the trained model to the given destination file
for (indep_hdrs, dep_hdr, (save_dest, accuracy_dest)) in modelParams:
    print("Training on dependent variable \'" + dep_hdr + "\'")
    train_model_and_dump(indep_hdrs, dep_hdr, save_dest, accuracy_dest)

