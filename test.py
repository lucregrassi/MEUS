import random
import numpy as np
from scipy.stats import halfnorm

np.random.seed(69)
print(np.random.randint(6))
print(np.random.randint(0,10))
rv = halfnorm.rvs(loc=0, scale=0.7, size=100)

print(np.random.randint(0,10))
