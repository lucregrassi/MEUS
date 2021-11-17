# #import os package to use file related methods
import os
import pandas as pd
import requests
import json
import csv
import statistics
import random
from pprint import pprint
# from owlready2 import *
from matplotlib import pyplot as plt
import numpy as np
import math
import itertools
from sketch import lis, Compute_dist


# BASE = "http://127.0.0.1:5000/"

# response = requests.delete(BASE + "IE/1" )
# # res = response.json()

# outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/'
outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/exps/Amatrice/100agents/10000loopsthDist/10%gateways/90%err_rate/'

fields = [ 'distance', 'CVR', 'Kalpha']

files = [file for file in os.listdir(outpath) if file.endswith('.csv')]

# print(len(files))
# input()

# for file in files:
#         if not file.split('.')[0].isdigit():
#             files.remove(file)

# print(files)
# input()

# cvr       = [float(pd.read_csv(outpath + file)['CVR'][i]) for file in files for i in range(len(pd.read_csv(outpath + file)['CVR'])) if float(pd.read_csv(outpath + file)['CVR'][i])!=-2] 
# dist      = [float(pd.read_csv(outpath + file)['distance'][i]) for file in files for i in range(len(pd.read_csv(outpath + file)['distance']))]
# Kalpha    = [float(pd.read_csv(outpath + file)['Kalpha'][i]) for file in files for i in range(len(pd.read_csv(outpath + file)['Kalpha']))]

cvr = [[float(pd.read_csv(outpath + file)['CVR'][i]) if float(pd.read_csv(outpath + file)['CVR'][i])!=-2 else None for i in range(len(pd.read_csv(outpath + file)['CVR'])) ] for file in files] 
# # cvr = [batch for batch in cvr if batch]


dist = [[float(pd.read_csv(outpath + file)['distance'][i]) for i in range(len(pd.read_csv(outpath + file)['distance']))] for file in files]
# pprint(dist)
# input("cheeky")

Kalpha = [[float(pd.read_csv(outpath + file)['Kalpha'][i]) for i in range(len(pd.read_csv(outpath + file)['Kalpha']))] for file in files]
# print(Kalpha)

obss    = [[list(eval(pd.read_csv(outpath + file)['observations'][i])) for i in range(len(pd.read_csv(outpath + file)['distance']))] for file in files]
gts     = [dict(eval(pd.read_csv(outpath + file)['ground_truth'][0])) for file in files]



plt.style.use('seaborn-whitegrid')

count = 0
for i in [int(file.split('.')[0]) for file in files]:
    print(i)

    # print(count)
    if len(dist[count])>1:
        plt.figure(i)

        # if i==30:
        #     gt_in_obss = gts[count] in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][0]]
        #     gt_index = [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][0]].index(gts[count]) if gts[count] in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][0]] else None
        #     max_val_index = [obs['coders'] for obs in obss[count][0]].index(np.max([obs['coders'] for obs in obss[count][0]]))
        #     print('gt_in_obss:', gt_in_obss)
        #     print('gt_index:', gt_index)
        #     print('max_val_index:', max_val_index)
        #     print(gt_in_obss and max_val_index!=gt_index)

        #     if gts[count] not in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][0]]: #and\
        #         # [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][0]].index(gts[count])!=[obs['coders'] for obs in obss[count][0]].index(np.max([obs['coders'] for obs in obss[count][0]])):
        #         print("whats the issue!")
        #         print(Compute_dist(  obss[count][0][[obs['coders'] for obs in obss[count][0]].index(list(np.max(obs['coders'] for obs in obss[count][0]))[0])]['situation'],
        #                                 gts[count]['situation'],
        #                                 lis))
        #         print(Compute_dist(  obss[count][0][[obs['coders'] for obs in obss[count][0]].index(np.max([obs['coders'] for obs in obss[count][0]]))]['situation'],
        #                                 gts[count]['situation'],
        #                                 lis))
        #     input()

        plotted_to_be = [Compute_dist(  obss[count][n][[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))]['situation'],
                                        gts[count]['situation'],
                                        lis)
                                        if gts[count] not in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][n]]\
                                        or gts[count] in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][n]]\
                                        and [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][n]].index(gts[count])!=[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))\
                                        else\
                                        0 if gts[count] in [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][n]] and [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss[count][n]].index(gts[count])==[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))\
                                        else None\
                                        for n in range(len(dist[count]))]

        if None in plotted_to_be:
            print(plotted_to_be)
            input()

        plt.plot(plotted_to_be, label="dist")
        plt.plot(Kalpha[count], label='Kalpha', marker='*')

        if len(cvr[count])==0:
            for j,el in enumerate(dist[count]):
                plt.scatter(j,plotted_to_be[j], s=20, c='r', marker='o')
        else:
            for k,el in enumerate(dist[count]):

                if cvr[count][k]==None:
                    pass
                elif cvr[count][k]==0.:
                    plt.scatter(k,plotted_to_be[k], s=20, c='r', marker='o')
                
                elif cvr[count][k]==1 and len(list(eval(pd.read_csv(outpath + str(i) +'.csv')['observations'][k])))>1:
                    obss1    = list(eval(pd.read_csv(outpath + str(i) +'.csv')['observations'][k]))
                    gt1      = dict(eval(pd.read_csv(outpath + str(i) +'.csv')['ground_truth'][0]))
                    index   = [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss1 ].index(gt1)


                    # if the ground truth coincides with the majorly voted event
                    if index==[obs['coders'] for obs in obss1].index(np.max([obs['coders'] for obs in obss1])):
                        plt.scatter(k,0, s=20, color='green', marker='o')

                    elif index!=[obs['coders'] for obs in obss1].index(np.max(obs['coders'] for obs in obss1)):

                        plt.scatter(k,plotted_to_be[k], s=20, color='magenta', marker='o')

                elif cvr[count][k]==1 and len(list(eval(pd.read_csv(outpath + str(i) +'.csv')['observations'][k])))==1:
                    plt.scatter(k,0, s=20, color='green', marker='o')


        plt.legend(loc='upper left')
        plt.ylabel('metrics')
        plt.xlabel('# of obs')
        plt.axis()
        plt.tight_layout()
        # plt.show()
        plt.savefig(os.path.join(outpath+'plots/', str(i)+'.svg'))
        # input()
    count += 1

# print(len(cvr))
# print(len(dist))
# print(len(Kalpha))
# input()
# print("CVR:")
# print(round(statistics.mean(cvr), 3))
# print(round(statistics.stdev(cvr), 3))
# print("---")
# print("dist:")
# print(round(statistics.mean(dist), 3))
# print(round(statistics.stdev(dist), 3))
# print("---")
# print("Kalpha:")
# print(round(statistics.mean(Kalpha), 3))
# print(round(statistics.stdev(Kalpha), 3))
   



# for file in files:
#         if len(pd.read_csv(outpath + file)['distance'])>1:
#                 if len([val for val in pd.read_csv(outpath + file)['CVR'] if val!=-2])>1:
#                         print("---")
#                         print(file)
#                         print("---")
#                         with open('/Users/mario/Desktop/Fellowship_Unige/MEUS/'+file, 'w') as f:
#                                 writer = csv.DictWriter(f, fieldnames=fields)
#                                 writer.writeheader()


#                                 info = {
#                                         # 'Ncoders':      '/',
#                                         # 'who':          '/',
#                                         # 'when':         '/',
#                                         # 'what':         '/',
#                                         # 'observations': '/',
#                                         # 'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
#                                         'distance':    [round(statistics.mean(float(val) for val in pd.read_csv(outpath + file)['distance']), 3), round(statistics.stdev(float(val) for val in pd.read_csv(outpath + file)['distance']), 3)],
#                                         'CVR':          [round(statistics.mean(val for val in pd.read_csv(outpath + file)['CVR'] if val!=-2), 3), round(statistics.stdev(val for val in pd.read_csv(outpath + file)['CVR'] if val!=-2), 3)],
#                                         'Kalpha':       [round(statistics.mean(val for val in pd.read_csv(outpath + file)['Kalpha']), 3), round(statistics.stdev(val for val in pd.read_csv(outpath + file)['Kalpha']), 3)]
#                                 }
#                                 writer.writerow(info)
#                 else:
#                         print("---")
#                         print(file)
#                         print("---")
#                         with open('/Users/mario/Desktop/Fellowship_Unige/MEUS/'+file, 'w') as f:
#                                 writer = csv.DictWriter(f, fieldnames=fields)
#                                 writer.writeheader()



#                                 info = {
#                                         # 'Ncoders':      '/',
#                                         # 'who':          '/',
#                                         # 'when':         '/',
#                                         # 'what':         '/',
#                                         # 'observations': '/',
#                                         # 'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
#                                         'distance':    [round(statistics.mean(float(val) for val in pd.read_csv(outpath + file)['distance']), 3), round(statistics.stdev(float(val) for val in pd.read_csv(outpath + file)['distance']), 3)],
#                                         # 'CVR':          [statistics.mean(val for val in pd.read_csv(outpath + file)['CVR'] if val!=-2), statistics.stdev(val for val in pd.read_csv(outpath + file)['CVR'] if val!=-2)],
#                                         'Kalpha':       [round(statistics.mean(val for val in pd.read_csv(outpath + file)['Kalpha']), 3), round(statistics.stdev(val for val in pd.read_csv(outpath + file)['Kalpha']), 3)]
#                                 }
#                                 writer.writerow(info) 
