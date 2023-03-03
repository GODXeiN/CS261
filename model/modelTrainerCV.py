## Alternate version of the Model Trainer which uses GridSearch Cross-Validation to find a 
## locally-optimal "C" regularisation term for the model.

import pandas as pd
import numpy as np
from os.path import isdir
from os import makedirs

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression, SGDClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold

from projectDf import independent_headers, KEY_ID
from joblib import dump
import logregTrainer as Trainer

csvdata = "./data/trainDataStaged.csv"

# Open the project training/test data
df = pd.read_csv(csvdata)
print("Loaded Training File:", csvdata)

# Dependent field; the field we want to model to predict
target_attr = 'Success'


# If the model target directory is not present, make it
if not isdir(Trainer.TRAINED_MODEL_DIR):
    makedirs(Trainer.TRAINED_MODEL_DIR)


# Identify the groups (projects) from which each sample belongs
projectGroups = np.array(df[KEY_ID])
gkf = StratifiedGroupKFold(n_splits=10)



def train_model_and_dump(independent_headers, dependent_header, model_save_dest, model_accuracy_dest):

    # Get the independent data as a matrix
    x = np.array(df[independent_headers])
    y = np.array(df[dependent_header])
    
    # Hold back 20% of the dataset for validation
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y)

    # Define a range of C (regularisation) values to be tested in the tuning
    param_grid = {'C': [0.1, 1, 10, 100, 1000]} 

    # Initialise a Cross-Validation searcher to find the optimal C-value for a LogReg model
    grid = GridSearchCV(LogisticRegression(), param_grid, refit=True)

    # Apply standardisation to x before feeding to GridSearch to find optimal C
    scaler = StandardScaler().fit(X_train)
    X_train_norm = scaler.transform(X_train)
    # Note: no need to standardise y, since y is binary success/failure (0 or 1)
    grid.fit(X_train_norm, y_train)
    # Retrieve the C-value whose model produced the highest accuracy
    c_val = grid.best_estimator_.C
    print("Best C:", c_val)

    # Use the best C-value found by GridSearch to train a LogisticRegression model
    bestEstimator = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(C=c_val))])
    bestEstimator.fit(X_train, y_train)
    y_pred = bestEstimator.predict(X_test)

    # Get the mean-squared-error, a measure of the regression's error
    mse = mean_squared_error(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    print("MSE:",str(mse))
    print("Accuracy:", str(accuracy))

    print(classification_report(y_test, y_pred))

    # Export the trained model's accuracy (to evaluate likelihood of model's prediction being correct)
    Trainer.write_model_accuracy(y_test, y_pred, model_accuracy_dest)

    # Export the trained model to be loaded by other modules
    dump(bestEstimator, model_save_dest)



# Train a model for each of the identified target parameters, 
# dumping the trained model to the given destination file
for (indep_hdrs, dep_hdr, (save_dest, accuracy_dest)) in Trainer.modelParams:
    print("Training on dependent variable \'" + dep_hdr + "\'")
    train_model_and_dump(indep_hdrs, dep_hdr, save_dest, accuracy_dest)

