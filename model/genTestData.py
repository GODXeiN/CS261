from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 500
NUM_SAMPLES_PER_PROJECT = 1
BUDGET = (1, 10000, 1000)        # 1000 to 10 million
DEADLINE = (1, 2000)             # in days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)