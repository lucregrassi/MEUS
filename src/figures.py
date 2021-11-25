import os
import csv
import pandas as pd
import os, os.path
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint


plt.style.use('seaborn-whitegrid')
path_50="/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/experiments/50"
files_50 = os.listdir(path_50)


fifty = []

print(files_50)

files_50 = sorted(files_50)
print(files_50)


# files_50[0], files_50[1], files_50[2] = files_50[-3], files_50[-2], files_50[-1]

files_50[0], files_50[-3] = files_50[-3], files_50[0]
files_50[1], files_50[-2] = files_50[-2], files_50[1]
files_50[2], files_50[-1] = files_50[-1], files_50[2]

files_50[3], files_50[-3] = files_50[-3], files_50[3]
files_50[4], files_50[-2] = files_50[-2], files_50[4]
files_50[5], files_50[-1] = files_50[-1], files_50[5]
print(files_50)
# input()

for f in files_50:
    fifty.append(pd.read_csv("/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/experiments/50/" + str(f)))
    print(f)

print(fifty)


dbTab1mean_50   = []
dbTab1stdev_50  = []

dbTab2mean_50   = []
dbTab2stdev_50  = []

latency_mean = []
latency_stdev = []


for i in range(len(fifty)):
    dbTab1mean_50.append(fifty[i]['sizeTab1_mean'])
    dbTab1stdev_50.append(fifty[i]['sizeTab1_stdev'])

    dbTab2mean_50.append(fifty[i]['sizeTab2_mean'])
    dbTab2stdev_50.append(fifty[i]['sizeTab2_stdev'])

    latency_mean.append(fifty[i]['latency_mean'])
    latency_stdev.append(fifty[i]['latency_stdev'])

# print(dbTab1mean_50)
# print(len(fifty))
# for el in dbTab1mean_50:
#     print(el)
# input()

plt.figure(1)
plt.plot([416/20, 416/10, 416/5],dbTab1mean_50[-1::-3], c='b', label='9 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],dbTab1mean_50[-2::-3], c='tab:orange', label='6 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],dbTab1mean_50[-3::-3], c='k', label='3 hubs', linewidth=1.1)



plt.errorbar(416/20, dbTab1mean_50[-1],
                yerr=dbTab1stdev_50[-1], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12)
plt.errorbar(416/10, dbTab1mean_50[-4],
                yerr=dbTab1stdev_50[-4], elinewidth=0.8, ecolor='c',fmt='c^', capsize=12)
plt.errorbar(416/5, dbTab1mean_50[-7],
                yerr=dbTab1stdev_50[-7], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12)

plt.errorbar(416/20, dbTab1mean_50[-2],
                yerr=dbTab1stdev_50[-2], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12)
plt.errorbar(416/10, dbTab1mean_50[-5],
                yerr=dbTab1stdev_50[-5], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12)
plt.errorbar(416/5, dbTab1mean_50[-8],
                yerr=dbTab1stdev_50[-8], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12)

plt.errorbar(416/20, dbTab1mean_50[-3],
                yerr=dbTab1stdev_50[-3], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12)
plt.errorbar(416/10, dbTab1mean_50[-6],
                yerr=dbTab1stdev_50[-6], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12)
plt.errorbar(416/5, dbTab1mean_50[-9],
                yerr=dbTab1stdev_50[-9], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12)

plt.legend(loc='upper left')
plt.ylabel('db size [rows]')
plt.xlabel('events per node')

plt.figure(2)
plt.plot([416/20, 416/10, 416/5],dbTab2mean_50[-1::-3], c='b', label='9 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],dbTab2mean_50[-2::-3], c='tab:orange', label='6 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],dbTab2mean_50[-3::-3], c='k', label='3 hubs', linewidth=1.1)



plt.errorbar(416/20, dbTab2mean_50[-1],
                yerr=dbTab2stdev_50[-1], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12)
plt.errorbar(416/10, dbTab2mean_50[-4],
                yerr=dbTab2stdev_50[-4], elinewidth=0.8, ecolor='c',fmt='c^', capsize=12)
plt.errorbar(416/5, dbTab2mean_50[-7],
                yerr=dbTab2stdev_50[-7], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12, barsabove=False)

plt.errorbar(416/20, dbTab2mean_50[-2],
                yerr=dbTab2stdev_50[-2], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/10, dbTab2mean_50[-5],
                yerr=dbTab2stdev_50[-5], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/5, dbTab2mean_50[-8],
                yerr=dbTab2stdev_50[-8], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)

plt.errorbar(416/20, dbTab2mean_50[-3],
                yerr=dbTab2stdev_50[-3], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/10, dbTab2mean_50[-6],
                yerr=dbTab2stdev_50[-6], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/5, dbTab2mean_50[-9],
                yerr=dbTab2stdev_50[-9], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)

plt.legend(loc='upper left')
plt.ylabel('db size [rows]')
plt.xlabel('events per node')


plt.figure(3)
plt.plot([416/20, 416/10, 416/5],latency_mean[-1::-3], c='b', label='9 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],latency_mean[-2::-3], c='tab:orange', label='6 hubs', linewidth=1.1)
plt.plot([416/20, 416/10, 416/5],latency_mean[-3::-3], c='k', label='3 hubs', linewidth=1.1)


plt.errorbar(416/20, latency_mean[-1],
                yerr=latency_stdev[-1], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12, barsabove=False)
plt.errorbar(416/10, latency_mean[-4],
                yerr=latency_stdev[-4], elinewidth=0.8, ecolor='c',fmt='c^', capsize=12, barsabove=False)
plt.errorbar(416/5, latency_mean[-7],
                yerr=latency_stdev[-7], elinewidth=0.8, ecolor='c', fmt='c^', capsize=12, barsabove=False)


plt.errorbar(416/20, latency_mean[-2],
                yerr=latency_stdev[-2], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/10, latency_mean[-5],
                yerr=latency_stdev[-5], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/5, latency_mean[-8],
                yerr=latency_stdev[-8], elinewidth=0.8, ecolor='tab:orange', fmt='^', capsize=12, barsabove=False)


plt.errorbar(416/20, latency_mean[-3],
                yerr=latency_stdev[-3], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/10, latency_mean[-6],
                yerr=latency_stdev[-6], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)
plt.errorbar(416/5, latency_mean[-9],
                yerr=latency_stdev[-9], elinewidth=0.8, ecolor='dimgray', fmt='^', capsize=12, barsabove=False)

plt.legend(loc='upper left')
plt.xlabel('events per node')
plt.ylabel('latency time [s]')
plt.tight_layout()
plt.show()