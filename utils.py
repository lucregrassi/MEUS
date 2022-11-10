import csv
import copy
import argparse
import operator
import numpy as np
import pandas as pd
import krippendorff
from os import path
from owlready2 import *
# Forward compatibility for Python 3
from functools import reduce
import matplotlib.pyplot as plt
from glob import glob


def latency_plot(rad_gat):
    assert type(rad_gat) == str and (rad_gat == 'radius' or rad_gat == 'gateways'), \
        "The parameter over to which plot the graph shoud be either 'radius' or 'gateways' of type string."

    # assert os.path.exists(os.path.abspath(os.getcwd()) + '/lats_{0}/'.format(rad_gat)),\
    #     'You either have not set the flag -st to True when running the simulation or the parameter over which to plot the latencies is not the same one you chose for the simulation. Cannot plot latencies.'

    outpath = os.path.abspath(os.getcwd()) + '/'
    folders = sorted(glob(outpath + 'exp[0-5]'))

    files = [file for folder in folders for file in os.listdir(folder + '/lats')]
    num_of_files = len(files)

    assert num_of_files >= 3, \
        'You have to run at least 3 experiments first.'

    if rad_gat == 'radius':
        assert rad_gat == 'radius' and num_of_files >= 3, \
            'Number of latencies for the magnitude of the radius plot has to be at least 3.'
    else:
        assert rad_gat == 'gateways' and num_of_files >= 4, \
            'Number of latencies for the number of gateways parameter plot has to be at least 4.'

    latencies = [pd.read_csv(folder + '/lats/' + file)['lats'] for folder in folders for file in
                 os.listdir(folder + '/lats')] if rad_gat == 'gateways' \
        else [pd.read_csv(folder + '/lats/' + file)['lats'] for folder in folders for file in
              os.listdir(folder + '/lats')]

    plt.style.use('seaborn-whitegrid')
    plt.figure()

    if rad_gat == 'radius':
        plt.plot(latencies[0], label='{0}km radius'.format(files[0].split('.')[0][0]))
        plt.plot(latencies[1], label='{0}km radius'.format(files[1].split('.')[0][0]))
        plt.plot(latencies[2], label='{0}km radius'.format(files[2].split('.')[0][0]))

        plt.legend(loc='upper left')
        plt.ylabel('lat [#loops]')
        plt.xlabel('# of obs')

    else:
        plt.plot(latencies[0], label='latency {0}%'.format(files[0].split('.')[0]))
        plt.plot(latencies[1], label='latency {0}%'.format(files[1].split('.')[0]))
        plt.plot(latencies[2], label='latency {0}%'.format(files[2].split('.')[0]))
        plt.plot(latencies[3], label='latency {0}%'.format(files[3].split('.')[0]))

        plt.legend(loc='upper left')
        plt.ylabel('lat [#loops]')
        plt.xlabel('# of obs')

    plt.tight_layout()
    plt.savefig(path.join(outpath, "error_plot_{0}.svg".format(rad_gat)))


def plotter(agent, real_time_pos):
    xs = []
    ys = []
    for key in agent.path:
        xs.extend([agent.path[key]['UTM_coordinates'][0][0], agent.path[key]['UTM_coordinates'][1][0]])
        ys.extend([agent.path[key]['UTM_coordinates'][0][1], agent.path[key]['UTM_coordinates'][1][1]])
    for i in range(len(xs)):
        plt.scatter(xs[i], ys[i], s=20, c='k', marker='*')
    plt.plot(xs, ys, 'b-', label='path', linewidth=0.8)
    plt.scatter(real_time_pos[0], real_time_pos[1], s=30, c='r', marker='o')
    plt.axis('equal')
    plt.legend(loc='upper left')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.tight_layout()


def NewPreProcessing(json_data):
    data_ih = []  # list of dictionaries storing the exchange of the information
    data_do = []  # list of direct observation information

    for i in range(len(json_data) - 1):
        data_do.append({
            # 'dir_obs':  json_data[i][0]['what'],
            'situation': json_data[i][0]['what']['situation'],
            'obj': json_data[i][0]['what']['object'],
            'when': json_data[i][0]['when'],
            'where': json_data[i][0]['where'],
            'who': json_data[i][0]['id']
        })
        data_ih.append([])
        if len(json_data[i][1:]) > 0:
            for j in range(len(json_data[i][1:])):
                data_ih[i].append({
                    'observer': json_data[i][0]['id'],
                    'a1': json_data[i][1:][j][0],
                    'a2': json_data[i][1:][j][1],
                    'sender': json_data[-1]['db_sender'],
                    'where': json_data[i][1:][j][2],
                    'when': json_data[i][1:][j][3],
                    'sent_at_loop': json_data[-1]['time'],
                    'sent_where': json_data[-1]['sent_where']
                })
        else:
            data_ih[i].append({
                'observer': json_data[i][0]['id'],
                'a1': json_data[i][0]['id'],
                'a2': json_data[i][0]['id'],
                'sender': json_data[-1]['db_sender'],
                'where': json_data[i][0]['where'],
                'when': json_data[i][0]['when'],
                'sent_at_loop': json_data[-1]['time'],
                'sent_where': json_data[-1]['sent_where']
            })

    return data_do, data_ih, json_data[-1]['distances']


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


def NewIEtoDict(lis):
    lis[0] = lis[0].asdict()
    lis[0]['what'] = lis[0]['what'].asdict()

    if type(lis[0]['what']['event'][0]) == owlready2.entity.ThingClass:

        lis[0]['what'] = {'situation': str(lis[0]['what']['event'][0]).split(".", 1)[1],
                          'object': str(lis[0]['what']['event'][1]).split(".", 1)[1]
                          }
    else:
        lis[0]['what'] = {'situation': str(lis[0]['what']['event'][0]),
                          'object': str(lis[0]['what']['event'][1])
                          }
    return lis


def plot_agent_perf(agent, key, pth, e_rate):
    plt.style.use('seaborn-whitegrid')
    outpath = pth
    plt.figure(key)
    plt.plot([t[1] for t in agent.ordered_reps], [t[0] for t in agent.ordered_reps], marker='*', c='b', label='rep',
             linewidth=1.1)
    plt.plot([t[1] for t in agent.ordered_reps2], [t[0] for t in agent.ordered_reps2], marker='*', c='tab:orange',
             label='rep2', linewidth=1.1)
    # specifying horizontal line type
    plt.axhline(y=1 - e_rate, color='r', linestyle='-', linewidth=.4)
    plt.legend(loc='upper left')
    plt.ylabel('reps and rels')
    plt.xlabel('when')

    plt.tight_layout()
    plt.savefig(path.join(outpath, "agent_{0}.svg".format(int(key))))


# Stops iterating through the list as soon as it finds the value
def getIndexOfTuple(l, index, value):
    for pos, t in enumerate(l):
        if t[index] == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")


def sent_at_loop_plot(param):
    assert type(param) == str and param in ["gateways", "radius", "std_dev"], \
        "You have to choose a number from 1 to 3."

    outpath = os.path.abspath(os.getcwd()) + '/'
    folders = sorted(glob(outpath + 'exp[0-5]'))

    files = [file for folder in folders for file in os.listdir(folder + '/sent_to_db_loop')]
    num_of_files = len(files)

    assert num_of_files >= 3, 'You have to run at least 3 experiments first.'

    sent_to_db = [pd.read_csv(folder + '/sent_to_db_loop/' + file)['sent_to_db_loop'] for folder in folders for file in
                  os.listdir(folder + '/sent_to_db_loop')]

    plt.style.use('seaborn-whitegrid')
    plt.figure()

    if param == "gateways":
        plt.plot(sent_to_db[0], label='Gateways {0}%'.format(files[0].split('.')[0]))
        plt.plot(sent_to_db[1], label='Gateways {0}%'.format(files[1].split('.')[0]))
        plt.plot(sent_to_db[2], label='Gateways {0}%'.format(files[2].split('.')[0]))
        plt.plot(sent_to_db[3], label='Gateways {0}%'.format(files[3].split('.')[0]))
        plt.plot(sent_to_db[4], label='Gateways {0}%'.format(files[4].split('.')[0]))
        plt.plot(sent_to_db[5], label='Gateways {0}%'.format(files[5].split('.')[0]))
        plt.legend(loc='upper left')
        plt.ylabel('Simulation loops')
        plt.xlabel('Number of observations')

    elif param == 'radius':
        plt.plot(sent_to_db[0], label='{0}Km radius'.format(files[0].split('.')[0][0]))
        plt.plot(sent_to_db[1], label='{0}Km radius'.format(files[1].split('.')[0][0]))
        plt.plot(sent_to_db[2], label='{0}Km radius'.format(files[2].split('.')[0][0]))
        plt.plot(sent_to_db[3], label='{0}Km radius'.format(files[3].split('.')[0][0]))
        plt.plot(sent_to_db[4], label='{0}Km radius'.format(files[4].split('.')[0][0]))
        plt.plot(sent_to_db[5], label='{0}Km radius'.format(files[5].split('.')[0][0]))
        plt.legend(loc='upper left')
        plt.ylabel('Simulation loops')
        plt.xlabel('Number of observations')

    else:
        plt.plot(sent_to_db[0], label='Std dev {0}'.format(files[0].split('.')[0]))
        plt.plot(sent_to_db[1], label='Std dev {0}'.format(files[1].split('.')[0]))
        plt.plot(sent_to_db[2], label='Std dev {0}'.format(files[2].split('.')[0]))
        plt.plot(sent_to_db[3], label='Std dev {0}'.format(files[3].split('.')[0]))
        plt.plot(sent_to_db[4], label='Std dev {0}'.format(files[4].split('.')[0]))
        plt.plot(sent_to_db[5], label='Std dev {0}'.format(files[5].split('.')[0]))
        plt.plot(sent_to_db[6], label='Std dev {0}'.format(files[6].split('.')[0]))
        plt.plot(sent_to_db[7], label='Std dev {0}'.format(files[7].split('.')[0]))
        plt.plot(sent_to_db[8], label='Std dev {0}'.format(files[8].split('.')[0]))
        plt.legend(loc='upper left')
        plt.ylabel('Simulation loops')
        plt.xlabel('Number of observations')

    plt.tight_layout()
    plt.savefig(path.join(outpath, "sent_to_db_{0}.svg".format(param)))


def latency_meanStddev_plot(rep1_mean, rep1_stddev, rep2_mean, rep2_stddev, err_rate, pth):
    outpath = pth
    plt.style.use('seaborn-whitegrid')
    plt.figure(101)
    plt.plot(rep1_mean, label='rep1 mean', c='b')
    plt.plot(rep2_mean, label='rep2 mean', c='tab:orange')
    plt.axhline(y=1 - err_rate, color='r', linestyle='-', linewidth=.4)

    plt.legend(loc='upper left')
    plt.ylabel('mean ratings')
    plt.xlabel('# of observations')
    plt.tight_layout()
    plt.savefig(path.join(outpath, 'mean_rep_plot_{0}%.svg'.format(str(int((1 - err_rate) * 100)))))
    plt.figure(102)

    plt.plot(rep1_stddev, label='rep1 stddev', c='b')
    plt.plot(rep2_stddev, label='rep2 stddev', c='tab:orange')
    plt.legend(loc='upper left')
    plt.ylabel('stddev ratings')
    plt.xlabel('# of observations')
    plt.tight_layout()
    plt.savefig(path.join(outpath, 'stddev_rep_plot_{0}%.svg'.format(str(int((1 - err_rate) * 100)))))


def compute_Krippendorff_Alpha(node_info, n_gateways, normal_agent_weight, gateway_agent_weight):
    coders = list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))
    Nobs = len(node_info['obs'])
    history = list(itertools.chain(*node_info['rels']))
    rel_data = [list(itertools.chain([[1 if (i, coder) in history and coder == history[history.index((i, coder))][
        1] else 0 for i in range(Nobs)]] * normal_agent_weight)) \
                    if coder >= n_gateways else list(itertools.chain([[1 if (i, coder) in history and coder ==
                                                                            history[history.index((i, coder))][1] else 0
                                                                       for i in range(Nobs)]] * gateway_agent_weight)) for coder in coders]
    rel_data = [el for batch in rel_data for el in batch]
    rel_data = np.asarray(rel_data)
    rel_data = rel_data[[np.any(rel_data[k]) for k in range(len(rel_data))]]
    if len(rel_data[0]) == 1:
        return np.nan
    return krippendorff.alpha(reliability_data=rel_data, level_of_measurement='nominal')


def compute_CVR(node_info, n_gateways, normal_agent_weight, gateway_agent_weight):
    # Compute total number of voters based on their weight
    panel_size = np.sum([normal_agent_weight if coder > n_gateways else gateway_agent_weight for coder in
                         list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))])
    candidate = max(node_info['votes'])
    value = -2
    if panel_size in lawshe_values.keys():
        value = 0
        # if the threshold majority is reached
        if candidate >= lawshe_values[panel_size]:
            value = 1
    return value


def logger(ev_id, ag, when, node_info_, cvr, kalpha, outpath, fields, query_ev, n_gateways, distance,
           normal_agent_weight, gateway_agent_weight):
    node_info = copy.deepcopy(node_info_)
    for i, obs in enumerate(node_info['obs']):
        obs['coders'] = np.sum([normal_agent_weight if coder > n_gateways else gateway_agent_weight
                                for coder in node_info['whos'][i]])
    files = [file for file in os.listdir(outpath) if file.endswith('.csv')]
    # if I have only 1 coder the Kalpha value will be 1
    if np.isnan(kalpha) and len(node_info['obs']) == 1:
        kalpha = 1

    if ev_id + '.csv' in files:
        with open(ev_id + '.csv', 'a') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            info = {
                'Ncoders': np.sum([normal_agent_weight if coder > n_gateways else gateway_agent_weight for coder in
                                   list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))]),
                'who': ag,
                'when': when,
                'what': len(node_info['obs']) - 1,
                'observations': [obs for obs in node_info['obs']],
                # 'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
                'distance': distance,
                'CVR': cvr,
                'Kalpha': kalpha
            }
            writer.writerow(info)
    else:
        with open(ev_id + '.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            info = {
                'Ncoders': np.sum([normal_agent_weight if coder > n_gateways else gateway_agent_weight for coder in
                                   list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))]),
                'who': ag,
                'when': when,
                'what': len(node_info['obs']) - 1,
                'observations': [obs for obs in node_info['obs']],
                'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
                'distance': distance,
                'CVR': cvr,
                'Kalpha': kalpha
            }
            writer.writerow(info)


def parse_args():
    parser = argparse.ArgumentParser(description='''Application for running MEUS simulation''',
                                     usage=argparse.SUPPRESS,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-setup_map', default=False, type=bool,
                        help='If set to True initialize the map when the simulation is launched.')

    # Amatrice, Rieti, Lazio
    parser.add_argument('-place', default='Assisi, Perugia, Umbria', type=str,
                        help='Place where to run the simulation in the format (Town, Province, Region). Example: "Amatrice, Rieti, Lazio".')

    parser.add_argument('-hubs_4g', default=3, type=int,
                        help='number of hub for the 4g internet connection.')

    parser.add_argument('-radius_4g', default=2, type=int,
                        help='magnitude of the radius of each internet hub.')

    parser.add_argument('-n_agents', default=100, type=int,
                        help='number of agents present in the environment.')

    parser.add_argument('-gateway_ratio', default=0.3, type=float,
                        help='percentage of gateways agents present in the environment. Ex. if I want 30 percent of gateways agents: -n_gateways 0.3')

    parser.add_argument('-loop_distance', default=100, type=int,
                        help='distance in meters an agent travels each loop.')

    parser.add_argument('-seed', default=69, type=int,
                        help='random seed to obtain a specific experiment outcome.')

    parser.add_argument('-threshold', default=30, type=int,
                        help='percentage of events stored in the database to end the experiment.')

    parser.add_argument('-std_dev', default=1, type=float,
                        help='the higher the std dev the more agents will make wrong observations.')

    parser.add_argument('-std_dev_gateway', default=0.2, type=float,
                        help='the higher the std dev the more gateway agents will make wrong observations.')

    parser.add_argument('-nl', default=0, type=int,
                        help='The simulation will stop upon reaching nl number of loops instead of the percentage of seen events.')

    parser.add_argument('-epidemic', default=True, type=bool,
                        help='If set to True, agents will not exchange IEs with the same DO.')

    args = parser.parse_args()
    return args


# Content validity ratio critical values - Lawshe table
with open("cvr_fitting/lawshe_table.txt") as f:
    lawshe_values = {}
    lines = f.readlines()
    for line in lines:
        line = line.split()
        lawshe_values[int(line[0])] = int(line[1])
