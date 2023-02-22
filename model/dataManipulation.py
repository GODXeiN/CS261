# Shared Library providing common Data Manipulation functions used by multiple modules
 
import math


# Logistic function to compress values into the range [0,1]
def sigmoid_func(x):
    k = 5       # Steepness
    x_0 = 1     # Centered around 1
    exp = math.exp(-k*(x-x_0))
    return 1 / (1+exp)


# Convenience method for generating exponentially-distributed values for a given set of parameters/coefficients
# x_0 shifts curve parallel to x-axis
# k controls steepness of curve
# c shifts curve parallel to y-axis
def exponential(x, k, x_0, c):
    return math.exp(k*(x-x_0)) + c


# Performs floating-point division, while avoiding divide-by-zero errors
# If denominator is negative or 0, then result is 0
def calc_ratio_safe(num, denom):
    if denom > 0:
        return float(num) / float(denom)
    return 0