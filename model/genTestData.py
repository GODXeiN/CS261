from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 300
NUM_SAMPLES_PER_PROJECT = 1
BUDGET = (1, 500, 10000)        # 1000 to 10 million
DEADLINE = (100, 1000)             # in days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)