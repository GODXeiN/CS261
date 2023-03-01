## Generates an independent Dataset used to Test the Risk-Assessment Models.
## The budget/deadline for each project is generated randomly, within a specific range.
## See "genSampleData.py" for details about data sampling and export destination.

from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 200
NUM_SAMPLES_PER_PROJECT = 3
BUDGET = (1, 20, 10000)         # Range of project budgets (10,000 to 1 million, with step size 10k)
DEADLINE = (100, 300)           # Range of project length in Days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE, 0)