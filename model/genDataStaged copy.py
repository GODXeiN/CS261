from projectDf import SimProject
from os.path import isdir
from os import makedirs

# Generates a CSV file containing artificial project data.
# Simulates fixed number of projects then takes given number of samples from each
# and writes them to the given output file.

MODE_GEN_TRAIN = 0
MODE_GEN_TEST = 1

# If the data directory is not present, make it
if not isdir("./data"):
    makedirs("./data")

# Describes whether data should be generated for training or for testing the model
mode = MODE_GEN_TRAIN

FILE_TRAIN = "./data/trainDataStaged.csv" 
FILE_TEST = "./data/testDataStaged.csv"

# Number of simulated projects to be generated
NUM_PROJECTS = 200
# Number of samples saved from each generated project
NUM_SAMPLES = 1

if mode == MODE_GEN_TRAIN:
    destFilename = FILE_TRAIN
    print("Generating Training Data...")
    NUM_SAMPLES = 3
else:
    destFilename = FILE_TEST
    print("Generating Testing Data...")

destFile = open(destFilename, 'w')

# Range for the initial budget of the generated projects
budgetMin = 1     # 100,000
budgetMax = 10000   # 5 million
budgetUnit = 1000 

# Range for the initial deadline of the generated projects
deadlineMin = 50
deadlineMax = 2000

# Stats about the generated project data
totalSamples = 0
numSuccesses = 0
numFailures = 0
numCancellations = 0


# from regLabeller import SCORER_SAVE_DEST
# from pickle import load

# # Load the trained regression model for predicting project success
# scorer = load(open(SCORER_SAVE_DEST,"rb"))



for i in range(0, NUM_PROJECTS):
    p = SimProject(i,budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)

    # Simulate the project's development till either complete or cancelled
    p.simulate()
    # print(str(p))
    # print("-----")

    # Add each success value as a new column in the dataframe
    sampleDf = p.get_labelled_samples(NUM_SAMPLES)

    totalSamples += len(sampleDf)

    # Get the result of the project, so we can count the output ratios
    success = sampleDf.iloc[0]['Success']
    if success == 0:
        numFailures += 1
    elif success == 1:
        numSuccesses += 1
    else:
        numCancellations += 1

    # Write the given samples to the file
    destFile.write(sampleDf.to_csv(header=(i==0), lineterminator='\n'))

destFile.close()

# Display a summary after generation
print("\nGenerated", NUM_PROJECTS, "projects, producing", totalSamples, "samples")
print(" >>> Successes:", str(numSuccesses))
print(" >>> Failures:", str(numFailures))
print(" >>> Cancellations:", str(numCancellations))
