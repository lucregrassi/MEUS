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
from main_database3 import eventsTab

# onto = get_ontology("ontology/MEUS.owl")
# onto.load()

# if type(onto.Situation)==owlready2.entity.ThingClass:
#     print("sticaz")
# else:
#     print(type(onto.Situation))

# BASE = "http://127.0.0.1:5000/"

# response = requests.delete(BASE + "IE/1" )
# # res = response.json()


# def gaussian(x, mu, sig):
#     return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.))) / (math.sqrt(2*math.pi*np.power(sig, 2)))

# x_values = np.linspace(-12, 12, 120)
# # for mu, sig in [(-1, 1), (0, 2), (2, 3)]:
# py.plot(x_values, gaussian(x_values, 0, 4))
# py.plot(x_values, gaussian(x_values, 0, 1))

# py.show()



# rep_file = pd.read_csv('reputations.csv')

# reps = rep_file['reputation']

# mean_error_rate1 = statistics.mean(reps[:30])
# mean_error_rate2 = statistics.mean(reps[30:])

# print("mean_error_rate1:", mean_error_rate1)
# print("mean_error_rate2:", mean_error_rate2)



# random.seed(3)
# threshold = 100
# no  = []
# yes = []
# reps = {str(i):{'positive': 0, 'negative': 0, 'rating': 0.5} for i in range(threshold) }

# event = {'yes': 0, 'no': 0}

# rep_mean = []

# for i in range(threshold):

#     value = random.random()
#     # key = str(random.randrange(100))
#     key = str(i)
#     if value<=0.3:
#         no.append(0)
#         reps[key]['negative'] +=1
#         event['no'] += 1
#         # reps[key]['rating'] = event['no'] / (event['yes'] + event['no'])
#         # print(reps[key]['rating'])
#         # rep_mean.append(statistics.mean(reps[k]['rating'] for k in reps.keys() if reps[k]['rating']!=0.5))
#     else:
#         yes.append(1)
#         reps[key]['positive'] += 1
#         event['yes'] += 1
#         # reps[key]['rating'] = event['yes'] / (event['yes'] + event['no'])
#         # print(reps[key]['rating'])
#         # rep_mean.append(statistics.mean(reps[k]['rating'] for k in reps.keys() if reps[k]['rating']!=0.5))
    
#     print("i:", i)


# for j in range(threshold):

#     key = str(j)

#     # if reps[key]['positive'] > 0:
#     reps[key]['rating'] = event['yes'] / (event['yes'] + event['no']) 
#     # else:
#     #     reps[key]['rating'] = event['no'] / (event['yes'] + event['no'])

#     print(reps[key]['rating'])
#     # input()


# print(len(no))
# print(len(yes))

# print("No percentage:", len(no)/threshold*100)
# print("Yes percentage:", len(yes)/threshold*100)

# # print(reps['9999'])
# # print(reps['9998'])

# print(np.mean([reps[k]['rating'] for k in reps.keys() if reps[k]['negative']>0]))
# print(np.mean([reps[k]['rating'] for k in reps.keys() if reps[k]['positive']>0]))


# print("Error:", np.abs( (1-0.5)-rep_mean[-1]))

# plt.style.use('seaborn-whitegrid')

# plt.figure()

# plt.plot(rep_mean, label='rep')
# plt.axhline(y = 1-0.5, color = 'r', linestyle = '-', linewidth=.4)
# # plt.axhline(y = rep_mean[-1], color = 'k', linestyle = '-', linewidth=.4)

# plt.legend(loc='upper left')
# plt.ylabel('mean ratings')
# plt.xlabel('# of observations')
# plt.axis()
# plt.tight_layout()
# plt.show()

# outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/'
outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/exps/Amatrice/100agents/10000loopsthDist/20%gateways/100%err_rate/'

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

    print(count)
    if len(dist[count])>1:
        plt.figure(i)

        # pprint([[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]])
        # input()
        pprint([[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]])
        pprint(gts[count])
        gt = None
        if any(gts[count] in nest for nest in [[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]]):
            for nest in [[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]]:
                if gts[count] in nest:
                    gt = nest.index(gts[count])
                    break
        # gt = [[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]].index(gts[count]) if gts[count] in [[{'situation':obs[j]['situation'], 'object': obs[j]['object'] } for j in range(len(obs))] for obs in obss[count]] else None
        print(gt)
        plotted_to_be = [dist[count][n] if gt!=None and gt!=[obs['coders'] for obs in obss[count][n]].index(list(np.max(obs['coders'] for obs in obss[count][n]))[0]) and \
                len(obss[count][n])-1==[obs['coders'] for obs in obss[count][n]].index(list(np.max(obs['coders'] for obs in obss[count][n]))[0]) else 2 \
                    if gt==None else 0 for n in range(len(dist[count]))]
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

                    # pprint(obss)
                    # print(index)
                    # print([obs['coders'] for obs in obss])
                    # print(np.max([obs['coders'] for obs in obss]))
                    # print([obs['coders'] for obs in obss].index(np.max([obs['coders'] for obs in obss])))
                    # print(obss[index])
                    # print(type(obss[index]))
                    # print(obss[[obs['coders'] for obs in obss].index(np.max([obs['coders'] for obs in obss]))])
                    # print(type(obss[[obs['coders'] for obs in obss].index(np.max([obs['coders'] for obs in obss]))]))
                    # print([obs['coders'] for obs in obss].index(np.max([obs['coders'] for obs in obss]))==obss[index])

                    # if the ground truth coincides with the majorly voted event
                    if index==[obs['coders'] for obs in obss1].index(np.max([obs['coders'] for obs in obss1])):
                        plt.scatter(k,0, s=20, color='green', marker='o')

                    elif index!=[obs['coders'] for obs in obss1].index(np.max(obs['coders'] for obs in obss1)):

                        # ind = [obs['coders'] for obs in obss1].index(np.max(obs['coders'] for obs in obss1))
                        # lista = list(eval(pd.read_csv(outpath + str(i) +'.csv')['observations']))

                        # for l in range(len(lista)):
                        #     if len(lista[l])-1==ind:
                        #         d = dist[count][l]
                        #         break

                        plt.scatter(k,plotted_to_be[k], s=20, color='magenta', marker='o')

                elif cvr[count][k]==1 and len(list(eval(pd.read_csv(outpath + str(i) +'.csv')['observations'][k])))==1:
                    plt.scatter(k,0, s=20, color='green', marker='o')


        plt.legend(loc='upper left')
        plt.ylabel('metrics')
        plt.xlabel('# of obs')
        plt.axis()
        plt.tight_layout()
        # plt.show()
        plt.savefig(os.path.join('/Users/mario/Desktop/Fellowship_Unige/MEUS/', str(i)+'.svg'))
        # input()
    count += 1
        # plt.savefig(os.path.join('/Users/mario/Desktop/Fellowship_Unige/MEUS/', str(i)+'.csv'))


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
