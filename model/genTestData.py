## Generates an independent Dataset used to Test the Risk-Assessment Models.
## The budget/deadline for each project is generated randomly, within a specific range.
## See "genSampleData.py" for details about data sampling and export destination.

from genSampleData import generate_sample_data, MODE_GEN_TEST

NUM_PROJECTS = 200
NUM_SAMPLES_PER_PROJECT = 3
BUDGET = (100000, 1000000, 1)         # Range of project budgets (100k-400k, with step size 1k)
DEADLINE = (10, 500)                  # Range of project length in Days

generate_sample_data(MODE_GEN_TEST, NUM_PROJECTS, NUM_SAMPLES_PER_PROJECT, BUDGET, DEADLINE, 0)