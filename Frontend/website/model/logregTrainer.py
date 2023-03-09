## Original Trainer for the LogisticRegression models
## Note: this version should not be used since the Training samples for the same project may appear in both Train and Test Splits.
## Please use modelCrossTrainer or modelTrainerCV instead

import pandas as pd
import numpy as np
from os.path import isdir
from os import makedirs

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .projectDf import independent_headers
from joblib import dump
from os import getcwd


CSV_TRAINING_DATA = getcwd() + "/data/trainDataStaged.csv"

# Directory to which models are dumped
TRAINED_MODEL_DIR = getcwd() + "/trained/"

# The file to which the trained model will be saved
OVERALL_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'overallSuccessModel.joblib', TRAINED_MODEL_DIR + 'overallSuccessAccuracy.csv')
FINANCE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'financeModel.joblib', TRAINED_MODEL_DIR + 'financeAccuracy.csv')
CODE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'codeModel.joblib', TRAINED_MODEL_DIR + 'codeAccuracy.csv')
TIMESCALE_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'timescaleModel.joblib', TRAINED_MODEL_DIR + 'timescaleAccuracy.csv')
TEAM_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'teamModel.joblib', TRAINED_MODEL_DIR + 'teamAccuracy.csv')
MANAGEMENT_MODEL_SAVE_DEST = (TRAINED_MODEL_DIR + 'managementModel.joblib', TRAINED_MODEL_DIR + 'managementAccuracy.csv')

modelParams = [
    (independent_headers, 'Success', OVERALL_MODEL_SAVE_DEST),
    (independent_headers, 'Finance Success', FINANCE_MODEL_SAVE_DEST),
    (independent_headers, 'Timescale Success', TIMESCALE_MODEL_SAVE_DEST),
    (independent_headers, 'Code Success', CODE_MODEL_SAVE_DEST),
    (independent_headers, 'Team Success', TEAM_MODEL_SAVE_DEST),
    (independent_headers, 'Management Success', MANAGEMENT_MODEL_SAVE_DEST)
]


# Given the Expected results and the Model Predictions, write the model accuracy
# (True-Success-Rate and False-Failure-Rate) to the file with the given name
def write_model_accuracy(y_test, y_predict, targetFilename):
    classReport = classification_report(y_test, y_predict, output_dict=True)
    confMat = confusion_matrix(y_test, y_predict)

    trueFailure = confMat[0][0]     # Failures identified as a Failure
    falseFailure = confMat[0][1]    # Successes misidentified as a Failure
    falseSuccess = confMat[1][0]    # Failures misidentified as a Success
    trueSuccess = confMat[1][1]     # Successes identified as a Success
    
    # Likelihood the model correctly identifies a successful project 
    #   i.e. the True-Success-Rate; the precision of the Success class 
    trueSuccessRate = trueSuccess / (trueSuccess + falseFailure)

    # Likelihood the model identifies a successful project as a failure
    #   i.e. the False-Failure-Rate; the False-Positive-Rate of the Failure class
    falseFailureRate = falseFailure / (trueSuccess + falseFailure)

    # print("TSR:", str(trueSuccessRate))
    # print("FFR:", str(falseFailureRate))

    # Write the accuracy to the target file in CSV format
    accuracyFile = open(targetFilename, "w")
    accuracyFile.write("TSR,FFR\n")
    accuracyFile.write(str(trueSuccessRate) + "," +  str(falseFailureRate))
    accuracyFile.close()


# Train the model to predict the given dependent-header, when receiving values for the independent headers.
# Then, export the model to the file at model_save_dest and write its accuracy to the file at model_accuracy_dest.
def train_model_and_dump(indep_headers, dep_header, model_save_dest, model_accuracy_dest):

    # Get the independent data as a matrix
    x = np.array(df[indep_headers])
    y = np.array(df[dep_header])

    # Sequence a scaler and the model, so any input data is normalised before being fed to the model
    pipeLR = Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])

    # Split the imported data into training and test components
    # Stratify ensures that the proportion of each class is maintained
    # e.g. if the data contains 25% success, then training contains 25% success and test data contains 25% success
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1, stratify=y)
    # print("Split dataset into stratified training and test samples")

    # TRAINING using training dataset
    pipeLR.fit(X_train, y_train)
    # print("Trained model")

    # PREDICTION using test dataset
    y_pred = pipeLR.predict(X_test)
    # print("Obtained model predictions for test-set")

    # Evaluate the model's accuracy by comparing the prediction to the actual test y-values
    print(classification_report(y_test, y_pred))
    modelAccuracy = accuracy_score(y_test, y_pred)
    print(" >>> Accuracy:", str(modelAccuracy))

    write_model_accuracy(y_test, y_pred, model_save_dest)

    # Export the trained model for use by the Risk-Assessment system
    dump(pipeLR, model_save_dest)


# Run only if this file is called directly
if __name__ == "__main__":
    # Open the project training/test data
    df = pd.read_csv(CSV_TRAINING_DATA)
    print("Loaded Training File:", CSV_TRAINING_DATA)

    # Dependent field; the field we want to model to predict
    target_attr = 'Success'

    # If the model target directory is not present, make it
    if not isdir(TRAINED_MODEL_DIR):
        makedirs(TRAINED_MODEL_DIR)

    # Train a model for each of the identified target parameters, 
    # dumping the trained model to the given destination file
    for (indep_hdrs, dep_hdr, (save_dest, accuracy_dest)) in modelParams:
        print("Training on dependent variable \'" + dep_hdr + "\'")
        train_model_and_dump(indep_hdrs, dep_hdr, save_dest, accuracy_dest)
