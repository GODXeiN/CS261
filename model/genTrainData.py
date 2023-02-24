from genSampleData import generate_sample_data, MODE_GEN_TRAIN

NUM_PROJECTS = 1000
NUM_SAMPLES_PER_PROJECT = 3
BUDGET = (1, 5000, 10000)         # 10000 to 5 million
DEADLINE = (50, 1000)             # in days

generate_sample_data(MODE_GEN_TRAIN, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)