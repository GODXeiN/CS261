import pandas as pd
import numpy as np
from os.path import isdir
from os import makedirs

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold

from projectDf import independent_headers, KEY_ID
from joblib import dump

TRAINED_MODEL_DIR = "./trained/"

# The file to which the trained model will be saved
OVERALL_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'overallSuccessLogreg.joblib', TRAINED_MODEL_DIR + 'overallSuccessAccuracy.txt')
FINANCE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'financeLogreg.joblib', TRAINED_MODEL_DIR + 'financeAccuracy.txt')
CODE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'codeLogreg.joblib', TRAINED_MODEL_DIR + 'codeAccuracy.txt')
TIMESCALE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'timescaleLogreg.joblib', TRAINED_MODEL_DIR + 'timescaleAccuracy.txt')
TEAM_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'teamLogreg.joblib', TRAINED_MODEL_DIR + 'teamAccuracy.txt')
MANAGEMENT_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'managementLogreg.joblib', TRAINED_MODEL_DIR + 'managementAccuracy.txt')

# After testing, write the model's accuracy to this file
OVERALL_MODEL_ACCURACY_DEST = 'logregmodelaccuracy.txt'

csvdata = "./data/trainDataStaged.csv"

# Open the project training/test data
df = pd.read_csv(csvdata)
print("Loaded Training File:", csvdata)

# Dependent field; the field we want to model to predict
target_attr = 'Success'


# If the model target directory is not present, make it
if not isdir(TRAINED_MODEL_DIR):
    makedirs(TRAINED_MODEL_DIR)


# Identify the groups (projects) from which each sample belongs
projectGroups = np.array(df[KEY_ID])
gkf = GroupKFold(n_splits=10)




def train_model_and_dump(independent_headers, dependent_header, model_save_dest, model_accuracy_dest):

    # Get the independent data as a matrix
    x = np.array(df[independent_headers])
    y = np.array(df[dependent_header])

    # Store the trained model with the most accurate performance
    bestEstimator = None
    bestScore = 0
    
    # Train the model on each data split, retaining the configuration with the most accuracy
    for train, test in gkf.split(x, y, groups=projectGroups):
        # Sequence a scaler and the model, so any input data is normalised before being fed to the model
        pipeLR = Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])
        

        x_train = x[train]
        y_train = y[train]
        x_test = x[test]
        y_test = y[test]

        # print(train)
        # print(test)
        # print(x_train)

        pipeLR.fit(x_train, y_train)
        modelScore = pipeLR.score(x_test, y_test)

        # Only retain the model which exhibits the highest score (most accurate)
        if modelScore > bestScore:
            bestEstimator = pipeLR
            bestScore = modelScore

    print("Best Score:", str(bestScore))
    
    # y_pred = bestEstimator.predict(x_test)

    # e.g. if the data contains 25% success, then training contains 25% success and test data contains 25% success
    # X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1, stratify=y)
    # print("Split dataset into stratified training and test samples")

    # TRAINING using training dataset
    # print("Trained model")

    # PREDICTION using test dataset
    # print("Obtained model predictions for test-set")

    # Evaluate the model's accuracy by comparing the prediction to the actual test y-values
    # print(classification_report(y_test, y_pred))

    accuracyFile = open(model_accuracy_dest, "w")
    accuracyFile.write(str(bestScore))
    accuracyFile.close() 

    # # Export the trained model for use by the Risk-Assessment system
    dump(bestEstimator, model_save_dest)
    # print("Dumped model")


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

