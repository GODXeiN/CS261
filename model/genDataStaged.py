import random
from projectDf import SimProject

# Generates a CSV file containing artificial project data.
# Simulates fixed number of projects then takes given number of samples from each
# and writes them to the given output file.


file = open("testDataStaged.csv", 'w')

# Projects to be generated
NUM_PROJECTS = 500
# Number of sample states to record for each project
NUM_SAMPLES = 5

# Range for the initial budget of the generated projects
budgetMin = 1     # 100,000
budgetMax = 100   # 10 million
budgetUnit = 10000 

# Range for the initial deadline of the generated projects
deadlineMin = 100
deadlineMax = 1000

# Stats about the generated project data
totalSamples = 0
numSuccesses = 0
numFailures = 0
numCancellations = 0


for i in range(0, NUM_PROJECTS):
    p = SimProject(i,budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)
    # Simulate the project's development till either complete or cancelled
    p.simulate()
    # print(str(p))
    
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
    file.write(sampleDf.to_csv(header=(i==0), lineterminator='\n'))

file.close()

# Display a summary after generation
print("\nGenerated", NUM_PROJECTS, "projects, producing", totalSamples, "samples")
print(" >>> Successes:", str(numSuccesses))
print(" >>> Failures:", str(numFailures))
print(" >>> Cancellations:", str(numCancellations))
