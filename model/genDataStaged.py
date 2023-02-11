import random
from projectDf import Project, populate_evaluation_coefficients

# Generates a CSV file containing artificial project data
# Considers project state at various points in development (incomplete)

# file = open("testData.csv", 'w')

# Projects to generate
n = 1

# Units: 100k
budgetMin = 1     # 100,000
budgetMax = 100   # 10 million
budgetUnit = 100000 

# Length of the shortest possible project
deadlineMin = 200
# Length of the longest possible project
deadlineMax = 1000

# headers = Project().get_headers()
# hdrLine = headers[0]
# for i in range(1, len(headers)):
#     hdrLine += "," + headers[i]
# file.write(hdrLine+"\n")

populate_evaluation_coefficients()

for i in range(0, n):
    p = Project(budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)
    p.cancel()
    print(str(p))
    p.evaluate()
    # file.write(str(p)+"\n")

print("\nGenerated", n, "rows")