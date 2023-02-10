import pandas as pd
import numpy as np

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


df = pd.read_csv("testData.csv")

# Independent Fields; those we are given and asked to predict for
#   Note: if f features, we require f^2 samples to converge
features = ['Budget','Budget Tolerance','Communication','Average Team Experience','Team Size','Deadline','Days Taken','Cost']
# Dependent field; the field we want to model to predict
target_attr = 'Success'

# Get the independent data as a matrix
x = np.array(df[features])
y = np.array(df[target_attr])

logreg = LogisticRegression()

# Normalise the data and scale it to be within the range 0-1 
scaler = preprocessing.StandardScaler()
scaler.fit(x)
Input = scaler.transform(x)

# When success/failure is binary (0/1), we don't need to transform the output, so ignore this code
    # Encode the output labels between 0 and n-1 classes
    # le = preprocessing.LabelEncoder()
    # le.fit(y)
    # output = le.transform(y)
output = y

# Split the imported data into training and test components
# Stratify ensures that the proportion of each class is maintained
# e.g. if the data contains 25% success, then training contains 25% success and test data contains 25% success
X_train, X_test, y_train, y_test = train_test_split(Input, output, test_size=0.5, random_state=1, stratify=output)



# Actually train the model
logreg.fit(X_train, y_train)



# PREDICTION

# Test the model's prediction on the test set
y_pred = logreg.predict(X_test)

# Evaluate the model's accuracy by comparing the prediction to the actual test y-values
print(classification_report(y_test, y_pred))



# Manual Test (Can be removed)
# Creates a project, finds its success then gets the model to predict.

from projectOld import Project

p = Project()
p.budget = 1000000
p.budget_tolerance = 1.1
p.communication = 5
p.team_size = 2
p.avg_team_yrs = 5
p.deadline = 500
p.gen_result()
p.calc_success()

# Convert the project to an array, then to a matrix containing a single vector
proj_x = np.asarray(p.get_features(features)).reshape(1,-1)
# Normalise the input project vector
norm_x = scaler.transform(proj_x)

print("My Project: ", str(p))
# Get the prediction 
# (note: this is normalised, so if the output is not 0/1, we need to de-normalise it)
p_pred = logreg.predict(norm_x)
# p_act = le.inverse_transform(p_pred)

# Display prediction
if p_pred[0] == 1:
    print(" >>> LogReg prediction: Success (1)")
else:
    print(" >>> LogReg prediction: Failure (0)")
