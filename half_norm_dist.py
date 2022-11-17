from scipy.stats import halfnorm
import numpy as np
import math

np.random.seed(0)
rv = halfnorm.rvs(loc=0, scale=3, size=5)
#print(rv)
print(np.random.randint(500))

np.random.seed(0)
np.random.choice([0,1])
print("a",np.random.randint(500))

np.random.seed(0)
np.random.randint(2)
print("b",np.random.randint(500))

np.random.seed(0)
#np.random.choice([0])
print(np.random.randint(500))



np.random.seed(0)
rv = halfnorm.rvs(loc=0, scale=0.1, size=5)
print(np.random.randint(500))
#print(rv)
distances = []
for elem in rv:
    distances.append(math.floor(elem))

print(distances)

rv = halfnorm()
distribution = np.linspace(0, np.minimum(rv.dist.b, 3))
# print(distribution)
