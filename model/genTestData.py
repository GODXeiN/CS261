from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 500
NUM_SAMPLES_PER_PROJECT = 3
BUDGET = (1, 50, 10000)           # 10k to 500k
DEADLINE = (100, 800)             # in days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE)