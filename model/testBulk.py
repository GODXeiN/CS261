
from joblib import load
import pandas as pd
import numpy as np
from projectDf import independent_headers
from sklearn.metrics import classification_report, mean_squared_error
from logregTrainer import OVERALL_MODEL_SAVE_DEST, FINANCE_MODEL_SAVE_DEST, TIMESCALE_MODEL_SAVE_DEST, CODE_MODEL_SAVE_DEST, MANAGEMENT_MODEL_SAVE_DEST, TEAM_MODEL_SAVE_DEST


# Loads the artificial Test Dataset and all trained models
# Then, evaluates the performance of the model on the test dataset


print("\nBulk Testing Model...")

df = pd.read_csv("./data/testDataStaged.csv")


# Get the independent data as a matrix
x = np.array(df[independent_headers])
# Dependent field; the field we want to model to predict
y = np.array(df['Success'])


modelTests = [
    (FINANCE_MODEL_SAVE_DEST[0], 'Finance Success'),
    (TIMESCALE_MODEL_SAVE_DEST[0], 'Timescale Success'),
    (CODE_MODEL_SAVE_DEST[0], 'Code Success'),
    (MANAGEMENT_MODEL_SAVE_DEST[0], 'Management Success'),
    (TEAM_MODEL_SAVE_DEST[0], 'Team Success'),
    (OVERALL_MODEL_SAVE_DEST[0], 'Success')
]

# Display results in a table
print("\n" + "Model".ljust(30), "| ", "Accuracy".ljust(10), "| ", "MSE".ljust(10))
for (saveFile, targetAttr) in modelTests:
    model = load(saveFile)
    y_test = np.array(df[targetAttr])
    y_pred = model.predict(x)
    score = model.score(x, y_test)
    mse = mean_squared_error(y_test, y_pred)

    # Print out a new row for this model
    modelString = " * " + str(targetAttr)
    print(modelString.ljust(30), "| ", str(round(score,2)).ljust(10), "| ", str(round(mse,2)).ljust(10))


# Now, evaluate the performance of the Success prediction model
# Reload the Overall-Success model from the saved dump
pipeLR = load(OVERALL_MODEL_SAVE_DEST[0])

y_pred = pipeLR.predict(x)

print("\nOverall Performance:")
print(classification_report(y, y_pred))

# Get the model accuracy and write it to a file
result = pipeLR.score(x, y)
print("Overall accuracy:", str(result))
