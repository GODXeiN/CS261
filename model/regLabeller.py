import pandas as pd
import numpy as np

from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline


# A Regression Model which produces a success score label (1-5) based on various project attributes

# Run on balanced dataset (~45 datapoints)
df = pd.read_csv("../data/balancedSuccessFactors.csv")
# Run on complete dataset (~100 datapoints)
df = pd.read_csv("../data/allSuccessFactors.csv")

# Independent Fields; those we are given and asked to predict for
features = ['Top-Level Management Support','Project Planning', 'Team Commitment','Team Communication','Team Morale','Overall Expertise', 'Budget', 'Schedule']
# Dependent field; the field we want to model to predict
target_attr = 'Overall success'

# Get the independent data as a matrix
x = np.array(df[features])
y = np.array(df[target_attr])

# Datasets contain missing values, so apply K-Nearest neighbours 
# to infer missing values from their closest 2 neighbours
imputer = KNNImputer(n_neighbors=2, weights="uniform")
Input = imputer.fit_transform(x)

print(str(Input))

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
print("Predictions: ", y_pred)

# Evaluate the model's accuracy by comparing the prediction to the actual test y-values
print("MSE: ", mean_squared_error(y_test, y_pred))
