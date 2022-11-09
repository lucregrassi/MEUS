from scipy.stats import halfnorm
import math
import numpy as np

np.random.seed(seed=69)

rv = halfnorm.rvs(loc=0, scale=0.5, size=10)
print(rv)
np.random.seed(seed=69)
rv = halfnorm.rvs(loc=0, scale=0.5, size=1)
print(rv)
np.random.seed(seed=69)
rv = halfnorm.rvs(loc=0, scale=0.5, size=1)
print(rv)
np.random.seed(seed=69)
rv = halfnorm.rvs(loc=0, scale=0.2, size=1)
print(rv)
np.random.seed(seed=69)
rv = halfnorm.rvs(loc=0, scale=0.2, size=1)
print(rv)

