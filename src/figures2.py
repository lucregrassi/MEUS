import os
import csv
import pandas as pd
import os, os.path
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

plt.style.use('seaborn-whitegrid')

path = "/Users/mario/Desktop/Newexperiments/50%"

files = os.listdir(path)

# pprint(files)
files.remove('.DS_Store')
files = sorted(files)
pprint(files)
input()

files[0], files[1] = files[1], files[0]
files[3], files[4] = files[4], files[3]
files[6], files[7] = files[7], files[6]

# files[3], files[-3] = files[-3], files[3]
# files[4], files[-2] = files[-2], files[4]
# files[5], files[-1] = files[-1], files[5]
pprint(files)
input()

values = []

for f in files:
    values.append(pd.read_csv(path + "/" + str(f)))
    print(f)

print(values)
input()


dbTab1  = []
dbTab2  = []

# latency_mean = []
# latency_stdev = []
ratio = []

for i in range(len(values)):
    # dbTab1.append(values[i]['sizeTab1_mean'])
    # dbTab2.append(values[i]['sizeTab2_mean'])

    ratio.append(values[i]['sizeTab2_mean']/values[i]['sizeTab1_mean'])


plt.figure(1)
plt.plot([10, 30, 50],ratio[6::9], c='b', label='9 hubs', linewidth=1.1)
plt.plot([10, 30, 50],ratio[3:6], c='tab:orange', label='6 hubs', linewidth=1.1)
plt.plot([10, 30, 50],ratio[0:3], c='k', label='3 hubs', linewidth=1.1)

plt.legend(loc='upper left')
plt.ylabel('ratio db [rows]')
plt.xlabel('ration of nodes with an event')

plt.tight_layout()
plt.show()