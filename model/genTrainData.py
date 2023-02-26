from genSampleData import generate_sample_data, MODE_GEN_TRAIN

NUM_PROJECTS = 100
NUM_SAMPLES_PER_PROJECT = 5
BUDGET = (1, 3000000, 1)          # Range of project budgets (1000 to 3 million, with step size 1000)
DEADLINE = (1, 1500)              # Range of project length in days


BUDGET_MIN = 1
BUDGET_MAX = 3000000
BUDGET_RANGE = BUDGET_MAX - BUDGET_MIN
DEADLINE_MIN = 1
DEADLINE_MAX = 1500
DEADLINE_RANGE = DEADLINE_MAX - DEADLINE_MIN

# Defines how many sub-ranges the budget/deadline parameters are divided into for the generation calls
NUM_GROUPS = 5

# Split the ranges for budget and deadline into the given number of groups
BUDGET_GROUP_GAP = round(BUDGET_RANGE / NUM_GROUPS)
DEADLINE_GROUP_GAP = round(DEADLINE_RANGE / NUM_GROUPS)

projectID = 0

# Group-Based Data Generation
#   The ranges for Budget and Deadline are too large for randomly generated projects to adequately cover the ranges.
#   So, we divide those ranges into a fixed number of equal-sized intervals, and consider them in batches.
#   For each pair of Budget group and Deadline group, we generate a batch of data and write it to the file.
for i in range(0, NUM_GROUPS):
    budget_min = BUDGET_MIN + i * BUDGET_GROUP_GAP
    budget_max = budget_min + BUDGET_GROUP_GAP
    bdgt = (budget_min, budget_max, 1)

    # Then, for each budget range, consider each deadline range
    for j in range(0, NUM_GROUPS):
        deadline_min = DEADLINE_MIN + j * DEADLINE_GROUP_GAP
        deadline_max = deadline_min + DEADLINE_GROUP_GAP
        deadline = (deadline_min, deadline_max)

        index = i * NUM_GROUPS + j

        print("\nRunning Training Group", str(index), "with: budget=", str(bdgt) + ", deadline=", str(deadline))
        
        generate_sample_data(MODE_GEN_TRAIN, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, bdgt, deadline, projectID)
        # Store the ID of the next project to be generated, so we can append to the same file, rather than overwriting 
        projectID += NUM_PROJECTS