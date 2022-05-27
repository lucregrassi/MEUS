from scipy.stats import halfnorm
import numpy as np
import math

rv = halfnorm.rvs(loc=0, scale=3, size=100)
print(rv)
distances = []
for elem in rv:
    distances.append(math.floor(elem))

print(distances)

rv = halfnorm()
distribution = np.linspace(0, np.minimum(rv.dist.b, 3))
# print(distribution)
