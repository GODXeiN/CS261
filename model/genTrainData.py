
## Generates the Dataset used to Train the Risk-Assessment Models.
## The data is generated in batches, covering the range of budgets/deadlines.
## See "genSampleData.py" for details about data sampling and export destination.

from genSampleData import generate_sample_data, MODE_GEN_TRAIN

NUM_PROJECTS = 50
NUM_SAMPLES_PER_PROJECT = 3

BUDGET_MIN = 100
BUDGET_MAX = 1000000
DEADLINE_MIN = 10
DEADLINE_MAX = 100

BUDGET_RANGE = BUDGET_MAX - BUDGET_MIN
DEADLINE_RANGE = DEADLINE_MAX - DEADLINE_MIN

# Defines how many sub-ranges the budget/deadline parameters are divided into for the generation calls
# Note: all combinations are considered, batch numbers (N,M) actually result in N*M batches being computed.
NUM_BATCHES_BUDGET = 5
NUM_BATCHES_DEADLINE = 5

# Split the ranges for budget and deadline into the given number of groups
BUDGET_GROUP_GAP = round(BUDGET_RANGE / NUM_BATCHES_BUDGET)
DEADLINE_GROUP_GAP = round(DEADLINE_RANGE / NUM_BATCHES_DEADLINE)

# The ID of the first project to be generated
# If 0, then the CSV headers are written to the file also
# Otherwise, the projects are appended to the target file
projectID = 10000

# Stores the number of batches that have been generated including the current batch
batch_num = 0

# Group-Based Data Generation
#   The ranges for Budget and Deadline are too large for randomly generated projects to adequately cover the ranges.
#   So, we divide those ranges into a fixed number of equal-sized intervals, and consider them in batches.
#   For each pair of Budget group and Deadline group, we generate a batch of data and write it to the file.
for i in range(0, NUM_BATCHES_BUDGET):
    budget_min = BUDGET_MIN + i * BUDGET_GROUP_GAP
    budget_max = budget_min + BUDGET_GROUP_GAP

    # Tuple representing minimum possible budget, maximum possible budget and the step size
    bdgt = (budget_min, budget_max, 1)

    # Then, for each budget range, consider each deadline range
    for j in range(0, NUM_BATCHES_DEADLINE):
        deadline_min = DEADLINE_MIN + j * DEADLINE_GROUP_GAP
        deadline_max = deadline_min + DEADLINE_GROUP_GAP
        deadline = (deadline_min, deadline_max)

        batch_num += 1

        print("\nRunning Training Group", str(batch_num), "with: budget=" + str(bdgt) + ", deadline=" + str(deadline))
        
        generate_sample_data(MODE_GEN_TRAIN, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, bdgt, deadline, projectID)
        # Store the ID of the next project to be generated, so we can append to the same file, rather than overwriting 
        projectID += NUM_PROJECTS