
## Generates the Dataset used to Train the Risk-Assessment Models.
## The data is generated in batches, covering the range of budgets/deadlines.
## See "genSampleData.py" for details about data sampling and export destination.

from genSampleData import generate_sample_data, MODE_GEN_TRAIN

TOTAL_PROJECTS = 1000
NUM_SAMPLES_PER_PROJECT = 3
MAX_RECURSION_DEPTH = 5


# Generate the given number of projects randomly throughout the given interval (equally distributed)
def generate_uniformly(startProjectID, totalProjects, numBatchesBudget, numBatchesDeadline, budgetMin, budgetMax, deadlineMin, deadlineMax):
    # Split the ranges for budget and deadline into the given number of groups
    budgetBatchInterval = int(round((budgetMax - budgetMin) / numBatchesBudget))
    deadlineBatchInterval = int(round((deadlineMax - deadlineMin) / numBatchesDeadline))
    
    totalBatches = numBatchesBudget * numBatchesDeadline

    projectID = startProjectID

    projectsPerBatch = int(totalProjects / totalBatches)

    batchNum = 0

    # Group-Based Data Generation
    #   The ranges for Budget and Deadline are too large for randomly generated projects to adequately cover the ranges.
    #   So, we divide those ranges into a fixed number of equal-sized intervals, and consider them in batches.
    #   For each pair of Budget group and Deadline group, we generate a batch of data and write it to the file.
    for i in range(0, numBatchesBudget):
        batchBudgetMin = budgetMin + i * budgetBatchInterval
        batchBudgetMax = batchBudgetMin + budgetBatchInterval

        # Tuple representing minimum possible budget, maximum possible budget and the step size
        bdgt = (batchBudgetMin, batchBudgetMax, 1)

        # Then, for each budget range, consider each deadline range
        for j in range(0, numBatchesDeadline):
            batchDeadlineMin = deadlineMin + j * deadlineBatchInterval
            batchDeadlineMax = batchDeadlineMin + deadlineBatchInterval
            deadline = (batchDeadlineMin, batchDeadlineMax)

            batchNum += 1

            batchProgress = str(batchNum) + "/" + str(totalBatches)

            print("\nRunning Training Group", batchProgress , "with: budget=" + str(bdgt) + ", deadline=" + str(deadline))
            
            generate_sample_data(MODE_GEN_TRAIN, projectsPerBatch, NUM_SAMPLES_PER_PROJECT, bdgt, deadline, projectID)
            # Store the ID of the next project to be generated, so we can append to the same file, rather than overwriting 
            projectID += projectsPerBatch


# Generate a portion of the data uniformly, then recurse on the bottom left quadrant
def split_recurse(projectID, budgetMin, budgetMax, deadlineMin, deadlineMax, numProjects, depth):
    numBatchesBudget = 2
    numBatchesDeadline = 2

    # Split the ranges for budget and deadline into the given number of groups
    budgetBatchInterval = round((budgetMax - budgetMin) / numBatchesBudget)
    deadlineBatchInterval = round((deadlineMax - deadlineMin) / numBatchesDeadline)

    # The ID of the first project to be generated
    # If 0, then the CSV headers are written to the file also
    # Otherwise, the projects are appended to the target file

    print("Recursive Generation (N=" + str(numProjects) + ", Depth=" + str(depth) + ")")


    # If we're recursing, assign 15% of the projects to each quadrant and reserve the rest
    if depth > 0 and numProjects > 10:
        projectsPerQuadrant = int(0.125 * numProjects)
        uniformDistProjects = projectsPerQuadrant * 4
        generate_uniformly(projectID, uniformDistProjects, 2, 2, budgetMin, budgetMax, deadlineMin, deadlineMax)
        projectID += uniformDistProjects

        # Assign the remaining projects to the bottom-left quadrant
        budgetMaxNew = budgetMin + budgetBatchInterval
        deadlineMaxNew = deadlineMin + deadlineBatchInterval
        numProjectsNew = numProjects - uniformDistProjects
        split_recurse(projectID, budgetMin, budgetMaxNew, deadlineMin, deadlineMaxNew, numProjectsNew, depth-1)
    # Otherwise, assign all projects evenly across all four quadrants
    elif numProjects > 0:
        generate_uniformly(projectID, numProjects, 2, 2, budgetMin, budgetMax, deadlineMin, deadlineMax)

    
# Generate a portion of the data uniformly, then recurse on the bottom left quadrant
def generate_recursively(startProjectID, numProjects, budgetMin, budgetMax, deadlineMin, deadlineMax, depth):
    # Constrain depth, to ensure positive but not large
    depth = max(1, min(depth, MAX_RECURSION_DEPTH))
    split_recurse(startProjectID, budgetMin, budgetMax, deadlineMin, deadlineMax, numProjects, depth)


if __name__ == '__main__':    
    budgetMin = 1
    budgetMax = 2000000
    deadlineMin = 1
    deadlineMax = 2000
    totalProjects = 4000
    batchesBudget = 2
    batchesDeadline = 2
    generate_recursively(8000, totalProjects, budgetMin, budgetMax, deadlineMin, deadlineMax, 3)
    # generate_uniformly(6000, totalProjects, batchesBudget, batchesDeadline, budgetMin, budgetMax, deadlineMin, deadlineMax)