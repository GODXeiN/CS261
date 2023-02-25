from genSampleData import generate_sample_data, MODE_GEN_TRAIN

NUM_PROJECTS = 2000
NUM_SAMPLES_PER_PROJECT = 5
BUDGET = (10, 1000, 1000)          # 10000 to 1 million
DEADLINE = (25, 1000)             # in days

generate_sample_data(MODE_GEN_TRAIN, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)