from projectDf import SimProject
from os.path import isdir
from os import makedirs

# Generates a CSV file containing artificial project data.
# Simulates fixed number of projects then takes given number of samples from each
# and writes them to the given output file.

MODE_GEN_TRAIN = 0
MODE_GEN_TEST = 1

FILE_TRAIN = "./data/trainDataStaged.csv" 
FILE_TEST = "./data/testDataStaged.csv"

# Callable function to generate sample projects and write to the corresponding output file
def generate_sample_data(mode, num_projects, samples_per_project, budget, deadline):
    # Determine ranges for the budget and deadline of generated projects
    (budgetMin, budgetMax, budgetUnit) = budget
    (deadlineMin, deadlineMax) = deadline

    if num_projects < 1 or samples_per_project < 1:
        print("Error: invalid number of projects/samples")
        return
    
    if mode == MODE_GEN_TRAIN:
        destFilename = FILE_TRAIN
        infoTxt = "Generating Training Data..."
    elif mode == MODE_GEN_TEST:
        destFilename = FILE_TEST
        infoTxt = "Generating Testing Data..."
    else:
        print("Error: mode", str(mode), "not recognised")
        return

    # If the data directory is not present, make it
    if not isdir("./data"):
        print("Target directory for generated data not found; creating it")
        makedirs("./data")
        
    print(infoTxt, "(" + str(num_projects), "projects x", str(samples_per_project), "samples)")

    

    # Stats about the generated project data
    totalSamples = 0
    numSuccesses = 0
    numFailures = 0
    numCancellations = 0

    numFinanceSuccess = 0
    numTeamSuccess = 0
    numTimescaleSuccess = 0
    numManagementSuccess = 0
    numCodeSuccess = 0


    # Number of projects between progress updates (divide by 20 = every 5%)
    progressInterval = num_projects / 10

    csvToWrite = []

    for i in range(0, num_projects):
        p = SimProject(i,budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)

        # Simulate the project's development till either complete or cancelled
        p.simulate()
        # print(str(p))
        # print("-----")

        # Add each success value as a new column in the dataframe
        sampleDf = p.get_labelled_samples(samples_per_project)

        totalSamples += len(sampleDf)

        firstSample = sampleDf.iloc[0]
        # Get the result of the project, so we can count the output ratios
        success = firstSample['Success']
        if success == 0:
            numFailures += 1
        elif success == 1:
            numSuccesses += 1
        else:
            numCancellations += 1

        if firstSample['Finance Success'] == 1:
            numFinanceSuccess += 1
        if firstSample['Code Success'] == 1:
            numCodeSuccess += 1
        if firstSample['Management Success'] == 1:
            numManagementSuccess += 1
        if firstSample['Team Success'] == 1:
            numTeamSuccess += 1
        if firstSample['Timescale Success'] == 1:
            numTimescaleSuccess += 1

        # Display progress of the data generation
        if i % progressInterval == 0:
            progressFrac = str(i) + "/" + str(num_projects)
            print(" >>>", progressFrac, "(" + str(100 * i / num_projects) + "%)")
        
        csvToWrite.append(sampleDf.to_csv(header=(i==0), lineterminator='\n'))
    print(" >>> 100.0%")

    # Display a summary after generation
    print("\nGenerated", num_projects, "projects, producing", totalSamples, "samples")
    print(" >>> Successes:", str(numSuccesses) + "; Failures:", str(numFailures))
    # print(" >>> Cancellations:", str(numCancellations))

    print(" >>> Finance Successes:", str(numFinanceSuccess) + "/" + str(num_projects))
    print(" >>> Timescale Successes:", str(numTimescaleSuccess) + "/" + str(num_projects))
    print(" >>> Code Successes:", str(numCodeSuccess) + "/" + str(num_projects))
    print(" >>> Management Successes:", str(numManagementSuccess) + "/" + str(num_projects))
    print(" >>> Team Successes:", str(numTeamSuccess) + "/" + str(num_projects))

    print("\nWriting to CSV...")
    # Write the given samples to the file
    destFile = open(destFilename, 'w')
    for data in csvToWrite:
        destFile.write(data)
    destFile.close()
    print(" >>> Complete!")
