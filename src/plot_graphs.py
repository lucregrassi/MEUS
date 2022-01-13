import os
import csv
import math
import json
import random
import requests
import itertools
import statistics
import numpy as np
import pandas as pd
from pprint import pprint
from sketch import lis, Compute_dist
from matplotlib import pyplot as plt
from utils import latency_plot

def plot_metrics():
    
    outpath = os.path.abspath(os.getcwd()) + '/'

    try:
        if not os.path.exists(outpath + '/plots'):
            os.makedirs(outpath + '/plots')
    except OSError:
        print ('Error: Creating directory of data')

    fields = [ 'distance', 'CVR', 'Kalpha']

    files   = [file for file in os.listdir(outpath) if file.endswith('.csv')]
    cvr     = [[float(pd.read_csv(outpath + file)['CVR'][i]) if float(pd.read_csv(outpath + file)['CVR'][i])!=-2 else None for i in range(len(pd.read_csv(outpath + file)['CVR'])) ] for file in files] 
    dist    = [[float(pd.read_csv(outpath + file)['distance'][i]) for i in range(len(pd.read_csv(outpath + file)['distance']))] for file in files]
    Kalpha  = [[float(pd.read_csv(outpath + file)['Kalpha'][i]) for i in range(len(pd.read_csv(outpath + file)['Kalpha']))] for file in files]

    obss    = [[list(eval(pd.read_csv(outpath + file)['observations'][i])) for i in range(len(pd.read_csv(outpath + file)['distance']))] for file in files]
    gts     = [dict(eval(pd.read_csv(outpath + file)['ground_truth'][0])) for file in files]

    plt.style.use('seaborn-whitegrid')

    count = 0
    for i in [int(file.split('.')[0]) for file in files]:
        print(i)

        if len(dist[count])>1:
            plt.figure(i)

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

            plt.plot(list(map(str, [i for i in range(len(plotted_to_be))])), plotted_to_be, label="dist")
            plt.plot(list(map(str, [i for i in range(len(Kalpha[count]))])), Kalpha[count], label='Kalpha', marker='*')

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
            plt.savefig(os.path.join(outpath+'plots/', str(i)+'.svg'))
        count += 1

if __name__=='__main__':

    ''' plotting the profile of CVR and Kalpha for every single node'''
    plot_metrics()


    ''' plotting the curves of the latency over some other parameter:
        - percentage of gateways' agents
        - magnitude of the radius of the hub(s)'''

    x = input("Do you wish to plot also the latencies over some parameter ? [y/n]")

    assert x=='y' or x=='n', \
        'Input should be either y or n.'

    if x=='y':

        param = input("Over which other parameter do you wish to plot the metrics:\n\
            - percentage of gateways' agents\n\
            - magnitude of the radius of the hub(s) ? [gateways/radius]")
        
        latency_plot(param)