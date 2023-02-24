from genSampleData import generate_sample_data, MODE_GEN_TRAIN

NUM_PROJECTS = 5000
NUM_SAMPLES_PER_PROJECT = 20
BUDGET = (1, 1000, 1000)          # 10000 to 5 million
DEADLINE = (50, 1500)             # in days

generate_sample_data(MODE_GEN_TRAIN, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)