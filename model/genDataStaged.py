import random
from projectDf import Project, populate_evaluation_coefficients

# Generates a CSV file containing artificial project data
# Considers project state at various points in development (incomplete)


file = open("testDataStaged.csv", 'w')

# Projects to be generated
NUM_PROJECTS = 2000
# Number of sample states to record for each project
NUM_SAMPLES = 5

# Units: 100k
budgetMin = 1     # 100,000
budgetMax = 1000   # 10 million
budgetUnit = 10000 

# Length of the shortest possible project
deadlineMin = 100
# Length of the longest possible project
deadlineMax = 1000

populate_evaluation_coefficients()

totalSamples = 0

for i in range(0, NUM_PROJECTS):
    p = Project(i,budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)
    # Simulate the project's development till complete or cancelled
    p.simulate()
    # print(str(p))
    
    sampleDf = p.get_labelled_samples(NUM_SAMPLES)
    totalSamples += len(sampleDf)
    file.write(sampleDf.to_csv(header=(i==0), lineterminator='\n'))

file.close()
print("\nGenerated", NUM_PROJECTS, "projects, producing", totalSamples, "samples")
