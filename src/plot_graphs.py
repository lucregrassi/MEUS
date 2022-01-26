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
from collections import Counter
import logging
from glob import glob

# Create and configure logger
# logging.basicConfig(filename="prova2.log",
#                     level=logging.DEBUG)


def show_mean_and_stddev():

    outpath = os.path.abspath(os.getcwd()) + '/'
    folders = sorted(glob(outpath + 'exp[0-4]'))

    for folder in folders:
        try:
            if not os.path.exists(outpath + folder.split('/')[-1] + '/meanStddv'):
                os.makedirs(outpath + folder.split('/')[-1] + '/meanStddv')
        except OSError:
            print ('Error: Creating directory of data meanStddv.')

        exp_path = outpath + folder.split('/')[-1] + '/'

        files   = [file for file in os.listdir(exp_path) if file.endswith('.csv')]

        # cvr       = [float(pd.read_csv(outpath + file)['CVR'][i]) for file in files for i in range(len(pd.read_csv(outpath + file)['CVR'])) if float(pd.read_csv(outpath + file)['CVR'][i])!=-2] 
        cvr       = [[float(pd.read_csv(exp_path + file)['CVR'][i]) if float(pd.read_csv(exp_path + file)['CVR'][i])!=-2 else None for i in range(len(pd.read_csv(exp_path + file)['CVR'])) ] for file in files]
        dist      = [float(pd.read_csv(exp_path + file)['distance'][i]) for file in files for i in range(len(pd.read_csv(exp_path + file)['distance']))]
        Kalpha    = [float(pd.read_csv(exp_path + file)['Kalpha'][i]) for file in files for i in range(len(pd.read_csv(exp_path + file)['Kalpha']))]


        flatten_cvr = list(itertools.chain(*cvr))

        agree       = [dist[i] for i, el in enumerate(flatten_cvr) if el==1]
        disagree    = [dist[i] for i, el in enumerate(flatten_cvr) if el==0]

        x1 = 0
        x2 = 1

        d = Counter(flatten_cvr)


        a_mean      = round(statistics.mean(agree), 3) if d[x2]>=2 else None
        a_stddev    = round(statistics.stdev(agree), 3) if d[x2]>=2 else None

        da_mean     = round(statistics.stdev(disagree), 3) if d[x1]>=2 else None
        da_stddev   = round(statistics.stdev(disagree), 3) if d[x1]>=2 else None

        print(f"Value {x1} has been dtected {d[x1]} times")
        print(f"Value {x2} has been dtected {d[x2]} times")
        print(f"Mean distance and standard deviation for agreement are:\n {a_mean}, {a_stddev}")
        print(f"Mean distance and standard deviation for disagreement are:\n {da_mean}, {da_stddev}")

        with open(exp_path + '/meanStddv/agreement.csv', 'w') as f:
            writer = csv.DictWriter(f, ['mean', 'stddev', 'ratio'])
            writer.writeheader()

            writer.writerow({     'mean': a_mean,
                                'stddev': a_stddev,
                                'ratio':  str(round(d[x2]/(d[x2] + d[x1])*100, 2)) + '%'})

        with open(exp_path + '/meanStddv/disagreement.csv', 'w') as f:
            writer = csv.DictWriter(f, ['mean', 'stddev', 'ratio'])
            writer.writeheader()

            writer.writerow({     'mean': da_mean,
                                'stddev': da_stddev,
                                'ratio':  str(round(d[x1]/(d[x2] + d[x1])*100, 2)) + '%'})
            

def plot_metrics():
    
    outpath = os.path.abspath(os.getcwd()) + '/'
    folders = sorted(glob(outpath + 'exp[0-4]'))


    for folder in folders:
        try:
            if not os.path.exists(outpath + folder.split('/')[-1] + '/plots'):
                os.makedirs(outpath + folder.split('/')[-1] + '/plots')
        except OSError:
            print ('Error: Creating directory of data')

        fields = [ 'distance', 'CVR', 'Kalpha']
        exp_path = outpath + folder.split('/')[-1] + '/'

        files   = [file for file in os.listdir(exp_path) if file.endswith('.csv')]

        cvr     = [[float(pd.read_csv(exp_path + file)['CVR'][i]) if float(pd.read_csv(exp_path + file)['CVR'][i])!=-2 else None for i in range(len(pd.read_csv(exp_path + file)['CVR'])) ] for file in files] 
        dist    = [[float(pd.read_csv(exp_path + file)['distance'][i]) for i in range(len(pd.read_csv(exp_path + file)['distance']))] for file in files]
        Kalpha  = [[float(pd.read_csv(exp_path + file)['Kalpha'][i]) for i in range(len(pd.read_csv(exp_path + file)['Kalpha']))] for file in files]

        obss    = [[list(eval(pd.read_csv(exp_path + file)['observations'][i])) for i in range(len(pd.read_csv(exp_path + file)['distance']))] for file in files]
        gts     = [dict(eval(pd.read_csv(exp_path + file)['ground_truth'][0])) for file in files]

        plt.style.use('seaborn-whitegrid')

        count = 0
        for i in [int(file.split('.')[0]) for file in files]:

            if len(dist[count])>1:
                plt.figure(folder.split('/')[-1]+'_'+str(i))

                # plotted_to_be = [Compute_dist(  obss[count][n][[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))]['situation'],
                #                                 gts[count]['situation'],
                #                                 lis)
                #                                 if gts[count]['situation'] not in [obs['situation'] for obs in obss[count][n]]\
                #                                 or gts[count]['situation'] in [obs['situation'] for obs in obss[count][n]]\
                #                                 and [obs['situation'] for obs in obss[count][n]].index(gts[count]['situation'])!=[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))\
                #                                 else\
                #                                 0 if gts[count]['situation'] in [obs['situation'] for obs in obss[count][n]] and [obs['situation'] for obs in obss[count][n]].index(gts[count]['situation'])==[obs['coders'] for obs in obss[count][n]].index(np.max([obs['coders'] for obs in obss[count][n]]))\
                #                                 else None\
                #                                 for n in range(len(dist[count]))]
                
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
                
                # logging.debug(plotted_to_be)

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
                        
                        elif cvr[count][k]==1 and len(list(eval(pd.read_csv(exp_path + str(i) +'.csv')['observations'][k])))>1:
                            obss1    = list(eval(pd.read_csv(exp_path + str(i) +'.csv')['observations'][k]))
                            gt1      = dict(eval(pd.read_csv(exp_path + str(i) +'.csv')['ground_truth'][0]))
                            index   = [{'situation':obs['situation'], 'object': obs['object'] } for obs in obss1 ].index(gt1)

                            # if the ground truth coincides with the majorly voted event
                            if index==[obs['coders'] for obs in obss1].index(np.max([obs['coders'] for obs in obss1])):
                                plt.scatter(k,0, s=20, color='green', marker='o')

                            elif index!=[obs['coders'] for obs in obss1].index(np.max(obs['coders'] for obs in obss1)):

                                plt.scatter(k,plotted_to_be[k], s=20, color='magenta', marker='o')

                        elif cvr[count][k]==1 and len(list(eval(pd.read_csv(exp_path + str(i) +'.csv')['observations'][k])))==1:
                            plt.scatter(k,0, s=20, color='green', marker='o')


                plt.legend(loc='upper left')
                plt.ylabel('metrics')
                plt.xlabel('# of obs')
                plt.axis()
                plt.tight_layout()
                plt.savefig(os.path.join(exp_path+'plots/', str(i)+'.svg'))
            count += 1

if __name__=='__main__':

    '''Showing how many times agents agree and disagree on observations and their respective mean and stddev of the distance (how much an observation is different from the ground truth).'''
    show_mean_and_stddev()

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