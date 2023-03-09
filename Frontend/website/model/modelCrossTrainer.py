import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os.path import isdir
from os import makedirs

from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.metrics import PrecisionRecallDisplay

from projectDf import KEY_ID
from joblib import dump
from logregTrainer import modelParams, write_model_accuracy, CSV_TRAINING_DATA, TRAINED_MODEL_DIR

DISPLAY_PRECISION_RECALL = False

# Creates a Pipeline model (with data standardisation) and trains it with CrossValidation to 
# recognise the columns given by independent_headers and predict the column 'dependent_header'. 
# Then, exports the trained model and its accuracy score to the given destination files.
def train_model_and_dump(df, independent_headers, dependent_header, model_save_dest, model_accuracy_dest, gkf, projectGroups):
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
        pipeClassifier = Pipeline([('scaler', StandardScaler()), ('sgd', SGDClassifier())])

        # Get the data using the indexes produced by GroupKFold
        x_train = x[train]
        y_train = y[train]
        x_test = x[test]
        y_test = y[test]

        pipeClassifier.fit(x_train, y_train)
        calibrator = CalibratedClassifierCV(pipeClassifier, cv='prefit')
        model=calibrator.fit(x_train, y_train)

        # Train the model on the training split
        # Then get predictions for the test split
        y_pred = model.predict(x_test)

        # Get the model's accuracy (note: accuracy + mse = 1)
        modelScore = accuracy_score(y_test, y_pred)
        print("Accuracy Score:", str(modelScore))

        # Only retain the model which exhibits the highest score (most accurate)
        if modelScore > bestScore:
            bestEstimator = model
            bestScore = modelScore

    print("Best Score:", str(bestScore))

    y_pred = bestEstimator.predict(x)
    print(classification_report(y, y_pred))

    # Get the model performance as a dictionary, so we can extract its TP/TF/FP/FN rates
    write_model_accuracy(y, y_pred, model_accuracy_dest)

    # # Export the trained model for use by the Risk-Assessment system
    dump(bestEstimator, model_save_dest)

    if DISPLAY_PRECISION_RECALL:
        # Display the PR-Curve for the best-performing model for this field 
        display = PrecisionRecallDisplay.from_predictions(y, y_pred, name="SGDClassifier")
        _ = display.ax_.set_title("2-class Precision-Recall curve for " + dependent_header)
        plt.show()


def train_all_models():
    # Open the project training/test data
    df = pd.read_csv(CSV_TRAINING_DATA)
    print("Loaded Training File:", CSV_TRAINING_DATA)

    # If the model target directory is not present, make it
    if not isdir(TRAINED_MODEL_DIR):
        makedirs(TRAINED_MODEL_DIR)

    # Get the project ID from each row, so we can ensure that data from the 
    # same project does not appear in both training and test splits
    projectGroups = np.array(df[KEY_ID])

    # Make a Cross-Validation K-Fold Generator
    gkf = GroupKFold(n_splits=5)

    # Train a model for each of the identified target parameters, 
    # dumping the trained model to the given destination file
    for (indep_hdrs, dep_hdr, (save_dest, accuracy_dest)) in modelParams:
        print("Training on dependent variable \'" + dep_hdr + "\'")
        train_model_and_dump(df, indep_hdrs, dep_hdr, save_dest, accuracy_dest, gkf, projectGroups)




if __name__ == '__main__':
    train_all_models()
   

