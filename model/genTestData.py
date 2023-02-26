from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 50
NUM_SAMPLES_PER_PROJECT = 3
BUDGET = (1, 100, 10000)          # Range of project budgets (10,000 to 1 million, with step size 10k)
DEADLINE = (100, 500)             # Range of project length in Days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE, 0)