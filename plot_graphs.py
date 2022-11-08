import os
import csv
import itertools
import statistics
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from collections import Counter
from glob import glob
from utils import sent_at_loop_plot


def show_mean_and_stddev():
    outpath = os.path.abspath(os.getcwd()) + '/'
    folders = sorted(glob(outpath + 'exp[0-8]'))

    for folder in folders:
        try:
            if not os.path.exists(outpath + folder.split('/')[-1] + '/mean_std_dev'):
                os.makedirs(outpath + folder.split('/')[-1] + '/mean_std_dev')
        except OSError:
            print('Error: Creating directory of data mean_std_dev.')

        exp_path = outpath + folder.split('/')[-1] + '/csv/'
        files = [file for file in os.listdir(exp_path) if file.endswith('.csv')]

        cvr = [[float(pd.read_csv(exp_path + file)['CVR'][i]) if float(
            pd.read_csv(exp_path + file)['CVR'][i]) != -2 else None for i in
                range(len(pd.read_csv(exp_path + file)['CVR']))] for file in files]
        dist = [float(pd.read_csv(exp_path + file)['distance'][i]) for file in files for i in
                range(len(pd.read_csv(exp_path + file)['distance']))]
        Kalpha = [float(pd.read_csv(exp_path + file)['Kalpha'][i]) for file in files for i in
                  range(len(pd.read_csv(exp_path + file)['Kalpha']))]

        flatten_cvr = list(itertools.chain(*cvr))

        dist_agree = [dist[i] for i, el in enumerate(flatten_cvr) if el == 1]
        dist_disagree = [dist[i] for i, el in enumerate(flatten_cvr) if el == 0]

        Kalpha_agree = [Kalpha[i] for i, el in enumerate(flatten_cvr) if el == 1]
        Kalpha_disagree = [Kalpha[i] for i, el in enumerate(flatten_cvr) if el == 0]

        x1 = 0
        x2 = 1

        d = Counter(flatten_cvr)

        a_dmean = round(statistics.mean(dist_agree), 3) if d[x2] >= 2 else None
        a_dstddev = round(statistics.stdev(dist_agree), 3) if d[x2] >= 2 else None

        da_dmean = round(statistics.mean(dist_disagree), 3) if d[x1] >= 2 else None
        da_dstddev = round(statistics.stdev(dist_disagree), 3) if d[x1] >= 2 else None

        a_Kmean = round(statistics.mean(Kalpha_agree), 3) if d[x2] >= 2 else None
        a_Kstddev = round(statistics.stdev(Kalpha_agree), 3) if d[x2] >= 2 else None

        da_Kmean = round(statistics.mean(Kalpha_disagree), 3) if d[x1] >= 2 else None
        da_Kstddev = round(statistics.stdev(Kalpha_disagree), 3) if d[x1] >= 2 else None

        avg_path = outpath + folder.split('/')[-1]
        with open(avg_path + '/mean_std_dev/agreement.csv', 'w') as f:
            writer = csv.DictWriter(f, ['dist_mean', 'dist_stddev', 'Kalpha_mean', 'Kalpha_stddev', 'ratio'])
            writer.writeheader()
            try:
                ratio = str(round(d[x2] / (d[x2] + d[x1]) * 100, 2)) + '%'
            except ZeroDivisionError:
                ratio = "0%"
            writer.writerow({'dist_mean': a_dmean,
                             'dist_stddev': a_dstddev,
                             'Kalpha_mean': a_Kmean,
                             'Kalpha_stddev': a_Kstddev,
                             'ratio': ratio})

        with open(avg_path + '/mean_std_dev/disagreement.csv', 'w') as f:
            writer = csv.DictWriter(f, ['dist_mean', 'dist_stddev', 'Kalpha_mean', 'Kalpha_stddev', 'ratio'])
            writer.writeheader()

            try:
                ratio = str(round(d[x1] / (d[x2] + d[x1]) * 100, 2)) + '%'
            except ZeroDivisionError:
                ratio = "0%"
            writer.writerow({'dist_mean': da_dmean,
                             'dist_stddev': da_dstddev,
                             'Kalpha_mean': da_Kmean,
                             'Kalpha_stddev': da_Kstddev,
                             'ratio': ratio})

        with open(avg_path + '/mean_std_dev/average_latency.csv', 'w') as f:
            for file in os.listdir(folder + '/dir_obs_lats'):
                dir_obs_lat_mean = folder + '/dir_obs_lats/' + file
            lats = []
            with open(dir_obs_lat_mean) as file:
                for line in file.readlines()[1:]:
                    lats.append(int(line))
            avg = sum(lats) / len(lats)
            f.write(str(avg))


def plot_metrics():
    folders = sorted(glob(os.getcwd() + '/exp[0-8]'))

    for folder in folders:
        try:
            if not os.path.exists(folder + '/plots'):
                os.makedirs(folder + '/plots')
        except OSError:
            print('Error: Creating directory of data')
        csv_path = folder + "/csv/"
        files = [file for file in os.listdir(csv_path) if file.endswith('.csv')]

        cvr = [[float(pd.read_csv(csv_path + file)['CVR'][i]) if float(
            pd.read_csv(csv_path + file)['CVR'][i]) != -2 else None for i in
                range(len(pd.read_csv(csv_path + file)['CVR']))] for file in files]
        dist = [[float(pd.read_csv(csv_path + file)['distance'][i]) for i in
                 range(len(pd.read_csv(csv_path + file)['distance']))] for file in files]
        Kalpha = [[float(pd.read_csv(csv_path + file)['Kalpha'][i]) for i in
                   range(len(pd.read_csv(csv_path + file)['Kalpha']))] for file in files]

        obss = [[list(eval(pd.read_csv(csv_path + file)['observations'][i])) for i in
                 range(len(pd.read_csv(csv_path + file)['distance']))] for file in files]
        gts = [dict(eval(pd.read_csv(csv_path + file)['ground_truth'][0])) for file in files]

        plt.style.use('seaborn-whitegrid')

        count = 0
        for i in [int(file.split('.')[0]) for file in files]:
            if len(dist[count]) > 1:
                plt.figure(folder.split('/')[-1] + '_' + str(i))

                plotted_to_be = [dist[count][n]
                                 if gts[count]['situation'] not in [obs['situation'] for obs in obss[count][n]] \
                                    or gts[count]['situation'] in [obs['situation'] for obs in obss[count][n]] \
                                    and [obs['situation'] for obs in obss[count][n]].index(gts[count]['situation']) != [
                                        obs['coders'] for obs in obss[count][n]].index(
                    np.max([obs['coders'] for obs in obss[count][n]])) \
                                     else \
                                     0 if gts[count]['situation'] in [obs['situation'] for obs in obss[count][n]] and [
                                         obs['situation'] for obs in obss[count][n]].index(gts[count]['situation']) == [
                                              obs['coders'] for obs in obss[count][n]].index(
                                         np.max([obs['coders'] for obs in obss[count][n]])) \
                                         else None \
                                 for n in range(len(dist[count]))]

                plt.plot(list(map(str, [i for i in range(len(plotted_to_be))])), plotted_to_be, label="Distance of the most voted observation from the ground truth")
                plt.plot(list(map(str, [i for i in range(len(Kalpha[count]))])), Kalpha[count], label="Krippendorff's Alpha",
                         marker='*')

                if len(cvr[count]) == 0:
                    for j, el in enumerate(dist[count]):
                        plt.scatter(j, plotted_to_be[j], s=20, c='r', marker='o')
                else:
                    for k, el in enumerate(dist[count]):
                        if cvr[count][k] is None:
                            pass
                        elif cvr[count][k] == 0.:
                            plt.scatter(k, plotted_to_be[k], s=20, c='r', marker='o')
                        else:
                            obss1 = list(eval(pd.read_csv(csv_path + str(i) + '.csv')['observations'][k]))
                            gt1 = dict(eval(pd.read_csv(csv_path + str(i) + '.csv')['ground_truth'][0]))
                            try:
                                index = [{'situation': obs['situation'], 'object': obs['object']} for obs in obss1].index(
                                    gt1)
                            except ValueError:
                                index = -1
                            # if the ground truth coincides with the majorly voted event
                            if index == [obs['coders'] for obs in obss1].index(np.max([obs['coders'] for obs in obss1])):
                                plt.scatter(k, 0, s=20, color='green', marker='o')
                            else:
                                plt.scatter(k, plotted_to_be[k], s=20, color='magenta', marker='o')

                plt.legend(loc='upper left')
                plt.ylabel('Metrics')
                plt.xlabel('Number of observations')
                plt.axis()
                plt.tight_layout()
                plt.savefig(os.path.join(folder + '/plots/', str(i) + '.svg'))
            count += 1


if __name__ == '__main__':

    '''Showing how many times agents agree and disagree on observations and their respective mean and stddev of 
    the distance (how much an observation is different from the ground truth).'''
    show_mean_and_stddev()

    ''' plotting the profile of CVR and Kalpha for every single node'''
    plot_metrics()

    ''' plotting the curves of the latency over some other parameter:
        - percentage of gateways' agents
        - magnitude of the radius of the hub(s)'''

    # TODO: uncomment for graphs comparing the loop number at which observations have been sent
    # param = input("Over which other parameter do you wish to plot the metrics:\n\
    #     1 - Percentage of gateways' agents\n\
    #     2 - Magnitude of the radius of the hub(s)?\n\
    #     3 - Standard deviation of the distribution of the agents' error\n")
    # if param == "1":
    #     param = "gateways"
    # elif param == "2":
    #     param = "radius"
    # else:
    #     param = "std_dev"

    # sent_at_loop_plot(param)
