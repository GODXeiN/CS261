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

# Number of simulated projects to be generated
NUM_PROJECTS_GENERATED = 10
# Number of samples saved from each generated project
SAMPLES_PER_PROJECT = 1


# Callable function to generate sample projects and write to the corresponding output file
def generate_sample_data(mode):
    if mode == MODE_GEN_TRAIN:
        destFilename = FILE_TRAIN
        NUM_PROJECTS_GENERATED = 1000
        SAMPLES_PER_PROJECT = 1
        infoTxt = "Generating Training Data..."
    elif mode == MODE_GEN_TEST:
        destFilename = FILE_TEST
        NUM_PROJECTS_GENERATED = 500
        SAMPLES_PER_PROJECT = 1
        infoTxt = "Generating Testing Data..."
    else:
        print("Error: mode", str(mode), "not recognised")
        return

    # If the data directory is not present, make it
    if not isdir("./data"):
        print("Target directory for generated data not found; creating it")
        makedirs("./data")
        
    print(infoTxt, "(" + str(NUM_PROJECTS_GENERATED), "projects x", str(SAMPLES_PER_PROJECT), "samples)")

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


    # Number of projects between progress updates (divide by 20 = every 5%)
    progressInterval = NUM_PROJECTS_GENERATED / 10

    csvToWrite = []

    for i in range(0, NUM_PROJECTS_GENERATED):
        p = SimProject(i,budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)

        # Simulate the project's development till either complete or cancelled
        p.simulate()
        # print(str(p))
        # print("-----")

        # Add each success value as a new column in the dataframe
        sampleDf = p.get_labelled_samples(SAMPLES_PER_PROJECT)

        totalSamples += len(sampleDf)

        # Get the result of the project, so we can count the output ratios
        success = sampleDf.iloc[0]['Success']
        if success == 0:
            numFailures += 1
        elif success == 1:
            numSuccesses += 1
        else:
            numCancellations += 1

        # Display progress of the data generation
        if i % progressInterval == 0:
            print(" >>>", str(100 * i / NUM_PROJECTS_GENERATED) + "%")
        
        csvToWrite.append(sampleDf.to_csv(header=(i==0), lineterminator='\n'))
    print(" >>> 100.0%")

    # Display a summary after generation
    print("\nGenerated", NUM_PROJECTS_GENERATED, "projects, producing", totalSamples, "samples")
    print(" >>> Successes:", str(numSuccesses) + "; Failures:", str(numFailures))
    # print(" >>> Cancellations:", str(numCancellations))

    print("\nWriting to CSV...")
    # Write the given samples to the file
    destFile = open(destFilename, 'w')
    for data in csvToWrite:
        destFile.write(data)
    destFile.close()
    print(" >>> Complete!")
