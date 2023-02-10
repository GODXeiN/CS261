import random
from projectOld import Project

# Generates a CSV file containing artificial project data

file = open("testData.csv", 'w')

# Projects to generate
n = 10000

# Units: 100k
budgetMin = 1     # 100,000
budgetMax = 100   # 10 million
budgetUnit = 100000 

deadlineMin = 200
deadlineMax = 1000

headers = Project().get_headers()
hdrLine = headers[0]
for i in range(1, len(headers)):
    hdrLine += "," + headers[i]
file.write(hdrLine+"\n")

for i in range(0, n):
    p = Project()
    p.make(budgetMin, budgetMax, budgetUnit, deadlineMin, deadlineMax)
    # print(str(p))
    file.write(str(p)+"\n")

print("Generated", n, "rows")