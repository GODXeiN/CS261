import pandas as pd
import numpy as np

from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline



# A Regression Model which predicts a success score label (0-1) based on project attributes.
# The model is trained on sourced data, collected by surveying project managers and provided by the following source:
    # Garousi, V., Tarhan, A., Pfahl, D. et al. 
    # "Correlation of critical success factors with success of software projects: an empirical investigation."
    # Software Qual J 27, 429–493 (2019). https://doi.org/10.1007/s11219-018-9419-5
    # Available at: https://link.springer.com/article/10.1007/s11219-018-9419-5


# Indicates where the trained model will be saved to, for use in other modules
SCORER_SAVE_DEST = "regscorer.pkl"

# The local addresses of the files used to train the model
# The balanced data accounts for the number of successes for each respondent, but halves the number of samples.
# Clean files are those which contain no missing values and have had the "Overall success" column compressed to the range [0,1]
BALANCED_DATA_FILE = "./data/balancedSuccessFactors.csv"
BALANCED_DATA_FILE_CLEAN = "./data/balancedSuccessFactorsClean.csv"
ALL_DATA_FILE = "./data/allSuccessFactors.csv"
ALL_DATA_FILE_CLEAN = "./data/allSuccessFactorsClean.csv"

# Control which dataset is used to train the model
USE_BALANCED_DATA = 0
USE_ALL_DATA = 1
RUN_MODE = USE_ALL_DATA


if RUN_MODE == USE_BALANCED_DATA:
    sourceFilename = BALANCED_DATA_FILE
    cleanFilename = BALANCED_DATA_FILE_CLEAN
else:
    sourceFilename = ALL_DATA_FILE
    cleanFilename = ALL_DATA_FILE_CLEAN

# Run on balanced dataset (~45 datapoints)
df = pd.read_csv(sourceFilename)
# Run on complete dataset (~100 datapoints)
# df = pd.read_csv(ALL_DATA_FILE)

# Independent Fields; those we are given and asked to predict for
features = ['Top-Level Management Support','Project Planning', 'Team Commitment','Team Communication','Team Morale','Average Team Experience', 'Budget', 'Schedule']
# Dependent field; the field we want to model to predict
target_attr = 'Overall success'

# Get the independent data as a matrix
x = np.array(df[features])
y = np.array(df[target_attr])

# Datasets contain missing values, so apply K-Nearest neighbours 
# to infer missing values from their closest 2 neighbours
imputer = KNNImputer(n_neighbors=2, weights="uniform")
Input = imputer.fit_transform(x)


file = open(cleanFilename, "w")
dfClean = pd.DataFrame(x, columns = features)
y = np.divide(y, 5)
dfClean.insert(len(dfClean.columns), target_attr, y)
dfClean.to_csv(file, lineterminator='\n')
file.close()

# print(str(Input))

# Create a model pipeline to scale/normalise the input data, then apply regression
# K-Neighbours regression produces a continuous output value
pipe = Pipeline([('scaler', preprocessing.StandardScaler()), 
                 ('model', KNeighborsRegressor())])


# No need to encode the labels since we are using regression to predict a continuous value
output = y

# Split the imported data into training and test components
X_train, X_test, y_train, y_test = train_test_split(Input, output, test_size=0.1, random_state=1)

# Actually train the model
pipe.fit(X_train, y_train)

# PREDICTION

# Test the model's prediction on the test set
y_pred = pipe.predict(X_test)

# print(X_test)
# print("Predictions: ", y_pred)
# print("Actual:", y_test)

# Evaluate the model's accuracy by comparing the prediction to the actual test y-values
# print("MSE: ", mean_squared_error(y_test, y_pred))


from pickle import dump
dump(pipe, open(SCORER_SAVE_DEST, 'wb'))