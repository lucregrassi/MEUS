import csv
import os
from os import path
import pandas as pd
import matplotlib.pyplot as plt
from utils import latency_plot
from pprint import pprint


latencies = []
outpath = '/Users/mario/Desktop/Fellowship_Unige/experiments/100/Amatrice/28-06/seed57/3kmRad'

lat_30 = pd.read_csv(outpath + '/error_plot_30.0%.csv')
lat_50 = pd.read_csv(outpath + '/error_plot_50.0%.csv')
lat_70 = pd.read_csv(outpath + '/error_plot_70.0%.csv')
lat_90 = pd.read_csv(outpath + '/error_plot_90.0%.csv')

latencies.extend([lat_30['lats'], lat_50['lats'], lat_70['lats'], lat_90['lats']])


# pprint(latencies)

pprint(lat_30['lats'])
print(len(latencies))
input()

latency_plot(latencies, outpath)

# ''' script for plotting agents reputations with different methods '''

# def sorter(l):
#     for i, el in enumerate(l):
#         if el[1]=='.' and  l[i-1][0] < el[0] and l[i-1][1]!='.':
#             # print(l[i])
#             # print(l[i-1])
#             # input()
#             for x in range(i-1, 0, -1):
#                 if l[x][1]=='.' and l[x][0]<l[i][0]:
#                     # print("GOODIE")
#                     index = l.index(l[x])

#                     l.insert(index+1,l[i])
#                     del l[i+1]
#                     # print(l)
#                     break

#     return l


# outpath = '/Users/mario/Desktop/Fellowship_Unige/experiments/100/Amatrice/28-06/seed57/method'

# # error_rate = pd.read_csv(outpath + '1/err_rate')

# files = []

# for m in range(4):
    
#     files.append(os.listdir(outpath + str(m+1) + '/rep'))

#     # print(files[0])

#     # sorted(files[0], key=lambda a: a[0])

#     files[m].sort(key=lambda a: a[:2])

#     if m==0:
#         del files[m][0]

#     print(files[m])

#     sorter(files[m])

#     print(files[m])
#     print("#######################################")

#     # print(files[i])
#     # input()


# agents = []
# outpath2 = '/Users/mario/Desktop/Fellowship_Unige/experiments/100/Amatrice/28-06/seed57'
# plt.style.use('seaborn-whitegrid')

# for i in range(4):
#     agents.append({})
#     for a in files[0]:
#         if a[1]=='.':
#             key = a[0]
#             agents[i][key] = {'err_rate': [], 'rep': []}
#         else:
#             key = a[:2]
#             agents[i][key] = {'err_rate': [], 'rep': []}

#         agents[i][key]['err_rate'] = pd.read_csv(outpath + str(i+1) + '/err_rate/{0}.csv'.format(key))['error_rate']
#         agents[i][key]['rep']      = pd.read_csv(outpath + str(i+1) + '/rep/{0}.csv'.format(key))['reps']


# # print(len(agents[0]['0']['rep']))
# # plt.plot(agents[0]['0']['rep'], marker='*', label='error rate', linewidth=1.5)
# # plt.axhline(y = 0.85, color = 'r', linestyle = '-', linewidth=.4)
# # plt.legend(loc='upper left')
# # plt.ylabel('reps')
# # plt.xlabel('# of observations')
# # plt.tight_layout()
# # plt.show()
# # input()

# ''' Final plot '''
# # for j in range(4):
# for a in agents[0].keys():
    
#     plt.figure(a)
#     plt.plot(agents[0][a]['err_rate'], marker='*', label='error rate', linewidth=1.5 )
#     plt.plot(agents[0][a]['rep'], label='method 1', linewidth=.7)
#     plt.plot(agents[1][a]['rep'], label='method 2', linewidth=.7)
#     plt.plot(agents[2][a]['rep'], label='method 3', linewidth=.7)
#     plt.plot(agents[3][a]['rep'], label='method 4', linewidth=.7 )
#     plt.axhline(y = 0.85, color = 'r', linestyle = '-', linewidth=.4)

#     plt.legend(loc='upper left')
#     plt.ylabel('reps')
#     plt.xlabel('# of observations')
#     plt.tight_layout()
#     plt.savefig(path.join(outpath2,'agent_{0}.svg'.format(a)))


