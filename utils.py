import csv
import math
import json
from pprint import pprint
import operator
import random
import statistics
import krippendorff
from functools import reduce  # forward compatibility for Python 3
import matplotlib.pyplot as plt
import numpy as np
from owlready2 import *
from os import path
import copy 



def plotter(agent, realTimePos):
    xs = []
    ys = []
    for key in agent.path:
        xs.extend([agent.path[key]['UTM_coordinates'][0][0], agent.path[key]['UTM_coordinates'][1][0]])
        ys.extend([agent.path[key]['UTM_coordinates'][0][1], agent.path[key]['UTM_coordinates'][1][1]])
    for i in range(len(xs)):
        plt.scatter(xs[i], ys[i], s=20, c='k', marker='*')
    plt.plot(xs, ys, 'b-', label='path', linewidth=0.8)
    plt.scatter(realTimePos[0], realTimePos[1], s=30, c='r', marker='o')
    plt.axis('equal')
    plt.legend(loc='upper left')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.tight_layout()
    # plt.show()


#   Preprocessing function for the incoming PUT method
# def preProcessing(json_data):
#     data_ih = []    # list of dictionaries storying the exchange of the information
#     data_do = {}    # the direct observation information


#     print ("json_data: " +str(json_data))
#     print("type of json_data: " +str(type(json_data)))
#     print("json_data['what']: " + str(json_data['what']))
#     print("type(json_data['what']): " +str(type(json_data['what'])))


#     # Retrieving the Direct Observation information
#     prev_nest = json_data
#     next_nest = json_data.get('what')
#     i = 0

#     while( next(iter(next_nest)) != 'event'):

#         data_ih.append({})
#         data_ih[i]['a1']    = prev_nest['history'][0]
#         data_ih[i]['a2']    = prev_nest['history'][1]
#         data_ih[i]['where'] = prev_nest['where']
#         data_ih[i]['when']  = prev_nest['when']

#         # updating nesting levels
#         prev_nest = next_nest
#         next_nest = next_nest['what']

#         print("counter: "+str(i))
#         i += 1

#     data_do['dir_obs']   = next_nest['event']
#     data_do['when']      = prev_nest['when']
#     data_do['where']     = prev_nest['where']
#     data_do['who']       = prev_nest['id']

#     # flag = True if len(json_data['history']) > 2 else False

#     return data_do, data_ih


#   Preprocessing function for the incoming PUT method
def preProcessing(json_data):
    data_ih = []    # list of dictionaries storying the exchange of the information
    data_do = []    # list of direct observation informations

    print ("json_data: " +str(json_data))
    print("type of json_data: " +str(type(json_data)))

    i = 0
    for j in range(len(json_data)):
        # Retrieving the Direct Observation information
        # json_data[j] = json_data[j].asdict()
        prev_nest = json_data[j]
        next_nest = json_data[j].get('what')
        data_ih.append([])
        more_than_1_nest = False
        while( next(iter(next_nest)) != 'situation'):
            more_than_1_nest = True
            if not len(prev_nest['history'])==1:

                data_ih[j].append({
                    'observer': prev_nest['id'],
                    'a1':       prev_nest['history'][-2],
                    'a2':       prev_nest['history'][-1],
                    'sender':   json_data[0]['id'],
                    'where':    prev_nest['where'],
                    'when':     prev_nest['when']
                })
            else:
                # if the agent is actually the observer
                data_ih[j].append({
                    'observer': prev_nest['id'],
                    'a1':       prev_nest['history'][0],
                    'a2':       prev_nest['history'][0],
                    'sender':   json_data[0]['id'],
                    'where':    prev_nest['where'],
                    'when':     prev_nest['when']
                })
            # updating nesting levels
            # next_nest = next_nest.asdict()
            # pprint.pprint(next_nest)
            prev_nest = next_nest
            next_nest = next_nest['what']

            print("counter: "+str(i))
            i += 1

        data_do.append({})
        data_do[j]['dir_obs']   = prev_nest['what']
        data_do[j]['when']      = prev_nest['when']
        data_do[j]['where']     = prev_nest['where']
        data_do[j]['who']       = prev_nest['id']

        if not more_than_1_nest:
            data_ih[j].append({
                    'observer': prev_nest['id'],
                    'a1':       prev_nest['history'][0],
                    'a2':       prev_nest['history'][0],
                    'sender':   json_data[0]['id'],
                    'where':    prev_nest['where'],
                    'when':     prev_nest['when']
                })

    return data_do, data_ih


def NewpreProcessing(json_data):
    data_ih = []    # list of dictionaries storying the exchange of the information
    data_do = []    # list of direct observation informations

    for i in range(len(json_data)-1):
        data_do.append({
            # 'dir_obs':  json_data[i][0]['what'],
            'situation':    json_data[i][0]['what']['situation'],
            'obj':          json_data[i][0]['what']['object'],    
            'when':         json_data[i][0]['when'],
            'where':        json_data[i][0]['where'],
            'who':          json_data[i][0]['id']
        })
        data_ih.append([])
        if len(json_data[i][1:]) > 0:
            for j in range(len(json_data[i][1:])):
                data_ih[i].append({
                    'observer':     json_data[i][0]['id'],
                    'a1':           json_data[i][1:][j][0],
                    'a2':           json_data[i][1:][j][1],
                    'sender':       json_data[-1]['db_sender'],
                    'where':        json_data[i][1:][j][2],
                    'when':         json_data[i][1:][j][3],
                    'sent_at_loop': json_data[-1]['time'],
                    'sent_where':   json_data[-1]['sent_where']
                })
        else:
           data_ih[i].append({
                    'observer':     json_data[i][0]['id'],
                    'a1':           json_data[i][0]['id'],
                    'a2':           json_data[i][0]['id'],
                    'sender':       json_data[-1]['db_sender'],
                    'where':        json_data[i][0]['where'],
                    'when':         json_data[i][0]['when'],
                    'sent_at_loop': json_data[-1]['time'],
                    'sent_where':   json_data[-1]['sent_where']
                })

    return data_do, data_ih, json_data[-1]['distances']#, json_data[-1]['reputations'], json_data[-1]['reputations2'], json_data[-1]['reliabilities']#, \
            # json_data[-1]['ratings']


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


def IEtoDict(IE):
    IE = IE.asdict()
    IE['what'] = IE['what'].asdict()
    root = []
    root.append('what')

    # print("IE: " +str(IE))
    # input("checking")
    counter = 0
    while( next(iter(get_by_path(IE, root))) != 'event'):
        # updating nesting levels
        root.append('what')
        tmp = get_by_path(IE, root)
        set_by_path(    IE,
                        root,
                        tmp.asdict())
        # pprint.pprint(IE)
        
        print("counter: " +str(counter))
        counter += 1
    
    # convert the dir obs object into a dictionary
    root = ['what' for i in range(counter+1)]
    # print("########################################")
    # pprint.pprint(get_by_path(IE, root))
    # pprint.pprint(get_by_path(IE, root)['event'])
    # input("daje")

    set_by_path(    IE,
                    root,
                    {       'situation':    str(get_by_path(IE, root)['event'][0]).split(".", 1)[1],
                            'object':       str(get_by_path(IE, root)['event'][1]).split(".", 1)[1]
                        })

    # print("processed IE: " +str(IE))
    # input("cheeky check")
    return IE


def NewIEtoDict(lis):
    lis[0]  = lis[0].asdict()
    lis[0]['what']  = lis[0]['what'].asdict() 

    if type(lis[0]['what']['event'][0])==owlready2.entity.ThingClass:

        lis[0]['what'] = { 'situation':    str(lis[0]['what']['event'][0]).split(".", 1)[1],
                            'object':      str(lis[0]['what']['event'][1]).split(".", 1)[1]
                            }
    else:
        lis[0]['what'] = { 'situation':    str(lis[0]['what']['event'][0]),
                            'object':      str(lis[0]['what']['event'][1])
                            }

    # print(lis)
    # input("NewIEtooDict() check")
    return lis



# Return the value of the Gaussian probability function with mean mu
# and standard deviation sigma at the given x value.
def pdf(x, mu=0.0, sigma=1.0):
    x = float(x - mu) / sigma
    return math.exp(-x*x/2.0) / math.sqrt(2.0*math.pi) / sigma



def plot_reputations(obss):

    plt.style.use('seaborn-whitegrid')

    agents = []
    reps = []
    reps1 = []
    rels = []
    whens = []
    for i in range(len(obss['whos'])):
        for j in range(len(obss['whos'][i])):
            if obss['whos'][i][j] not in agents:

                agents.append(obss['whos'][i][j])
                reps.append([rep for rep in obss['reps'][i]])
                rels.append([rel for rel in obss['rels'][i]])
                reps1.append([rep1 for rep1 in obss['reps1'][i]])

                whens.append([when for when in obss['whens'][i]])


    print("whens:", whens)
    print("reps:", reps)
    print("reps1:", reps1)
    input()

    for k in range(len(agents)):

        plt.figure(k)

        plt.plot(whens[k], reps[k])
        plt.plot(whens[k], reps1[k])
        plt.plot(whens[k], rels[k])

    
    plt.legend(loc='upper left')
    plt.ylabel('reps and rels')
    plt.xlabel('whens')

    plt.tight_layout()
    plt.show()
    

def plot_agent_perf(agent, key, pth, e_rate):#, rep):

    plt.style.use('seaborn-whitegrid')

    outpath = pth

    plt.figure(key)

    plt.plot([t[1] for t in agent.ordered_reps], [t[0] for t in agent.ordered_reps], marker='*', c='b', label='rep', linewidth=1.1)
    plt.plot([t[1] for t in agent.ordered_reps2], [t[0] for t in agent.ordered_reps2], marker='*', c='tab:orange', label='rep2', linewidth=1.1)
    # plt.plot([t[1] for t in agent.ordered_rels], [t[0] for t in agent.ordered_rels], marker='*', c='k', label='rel', linewidth=.5)
    # specifying horizontal line type
    plt.axhline(y = 1-e_rate, color = 'r', linestyle = '-', linewidth=.4)


    plt.legend(loc='upper left')
    plt.ylabel('reps and rels')
    plt.xlabel('when')

    plt.tight_layout()
    plt.savefig(path.join(outpath,"agent_{0}.svg".format(int(key))))
    # plt.show()


# Stops iterating through the list as soon as it finds the value
def getIndexOfTuple(l, index, value):
    for pos,t in enumerate(l):
        if t[index] == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")


def ran_gen():

    rNUm = random.randrange(100)

    return (rNUm % 2)

def pr_gen():

    x = ran_gen()
    y = ran_gen()

    return(x & y)


def latency_plot(latencies, pth):

    # if len(latencies) < 4:
    #     raise Exception

    plt.style.use('seaborn-whitegrid')

    outpath = pth

    plt.figure()

    plt.plot(latencies[0], label='1km radius')
    plt.plot(latencies[1], label='3km radius')
    plt.plot(latencies[2], label='5km radius')
    # plt.plot(latencies[3], label='latency_90%')
    # plt.axhline(y = statistics.mean(latencies), color = 'r', linestyle = '-', linewidth=.4)

    plt.legend(loc='upper left')
    plt.ylabel('lat [#loops]')
    plt.xlabel('# of obs')

    plt.tight_layout()
    plt.savefig(path.join(outpath, "error_plot.svg"))


def latency_meanStddev_plot(rep1_mean, rep1_stddev, rep2_mean, rep2_stddev, err_rate, pth):

    outpath = pth

    plt.style.use('seaborn-whitegrid')

    plt.figure(101)

    plt.plot(rep1_mean, label='rep1 mean', c='b')
    plt.plot(rep2_mean, label='rep2 mean', c='tab:orange')

    plt.axhline(y = 1-err_rate, color = 'r', linestyle = '-', linewidth=.4)

    plt.legend(loc='upper left')
    plt.ylabel('mean ratings')
    plt.xlabel('# of observations')
    plt.tight_layout()
    plt.savefig(path.join(outpath, 'mean_rep_plot_{0}%.svg'.format(str(int((1-err_rate)*100)))))
    

    plt.figure(102)

    plt.plot(rep1_stddev, label='rep1 stddev', c='b')
    plt.plot(rep2_stddev, label='rep2 stddev', c='tab:orange')

    # plt.errorbar([i for i in range(len(rep1_mean))], rep1_mean, yerr=rep1_stddev, ecolor='b', capsize=5)
    # plt.errorbar([i for i in range(len(rep2_mean))], rep2_mean, yerr=rep2_stddev, ecolor='tab:orange', capsize=5)

    plt.legend(loc='upper left')
    plt.ylabel('stddev ratings')
    plt.xlabel('# of observations')
    plt.tight_layout()
    plt.savefig(path.join(outpath, 'stddev_rep_plot_{0}%.svg'.format(str(int((1-err_rate)*100)))))



def compute_KrippendorffAlpha(node_info, n_gateways):

    rel_data = []
    
    coders = list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))
    Nobs = len(node_info['obs'])
    history = list(itertools.chain(*node_info['rels']))
    rel_data = [list(itertools.chain([[1 if (i, coder) in history and coder==history[history.index( (i, coder))][1] else 0 for i in range(Nobs)]]*2))\
            if coder>=n_gateways else list(itertools.chain([[1 if (i, coder) in history and coder==history[history.index( (i, coder))][1] else 0 for i in range(Nobs)]]*6)) for coder in coders]

    # print(rel_data)
    # rel_data = [el if len(batch)==6 else batch for batch in rel_data for el in batch]
    rel_data = [el for batch in rel_data for el in batch]
    # print(rel_data)
    rel_data = np.asarray(rel_data)
    # print(rel_data)
    # print(type(rel_data[0]))
    # print(type(rel_data[0][0]))
    rel_data = rel_data[[ np.any(rel_data[k]) for k in range(len(rel_data))]]
    # print("---")
    if len(rel_data[0])==1:
        return np.nan


    return krippendorff.alpha(reliability_data=rel_data, level_of_measurement='nominal')


def compute_CVR(node_info, query_ev, CVR, n_gateways):

    # panel_size = len(list(np.unique(np.asarray(list(itertools.chain(*node_info['whos']))))))
    panel_size = np.sum([2 if coder>n_gateways else 6 for coder in list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))])
    candidate = max(node_info['votes'])
    # print(node_info['votes'])
    # print(candidate)
    # input()

    ev_id = str(query_ev.id)

    value = -2
    if panel_size in CVR.keys():
        value = 0
        # if the threshold majority is reached
        if candidate>=CVR[panel_size]:
        # print("event in node", ev_id, " is: ", node_info['obs'][node_info['votes'].index(candidate)])
            value = 1
            # if the reported observation match the actual event
            index = node_info['votes'].index(candidate)
            
            if query_ev.situation==node_info['obs'][index]['situation'] and query_ev.obj==node_info['obs'][index]['object']:
                value = 1
    return value

def logger(ev_id, ag, when, node_info_, cvr, kalpha, outpath, fields, query_ev, n_gateways, distance):
    # outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/'
    # fields = ['Ncoders', 'who', 'when', 'what', 'observations', 'CVR', 'Kalpha']

    node_info = copy.deepcopy(node_info_)


    for i, obs in enumerate(node_info['obs']):
        obs['coders'] = np.sum([2 if coder>n_gateways else 6 for coder in node_info['whos'][i]])
    files = [file for file in os.listdir(outpath) if file.endswith('.csv')]

    if np.isnan(kalpha) and len(node_info['obs'])==1:
        kalpha=1

    if ev_id+'.csv' in files:

        # f = False
        # if ev_id=='108':
        # # if np.sum([2 if co >n_gateways else 6 for coder in list(np.unique(np.asarray(list(itertools.chain(*prior)))))])==4:
        #     # f = True
        #     pprint(node_info['whos'])
        #     pprint(node_info['obs'])
        #     input("yooooo")

        with open(ev_id+'.csv', 'a') as f:
            writer = csv.DictWriter(f, fieldnames=fields)

            info = {
                'Ncoders':      np.sum([2 if coder>n_gateways else 6 for coder in list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))]),
                'who':          ag,
                'when':         when,
                'what':         len(node_info['obs'])-1,
                'observations': [obs for obs in node_info['obs']],
                # 'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
                'distance':     distance,
                'CVR':          cvr,
                'Kalpha':       kalpha     

            }
            writer.writerow(info)


    else:
        with open(ev_id+'.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            info = {
                        'Ncoders':      np.sum([2 if coder>n_gateways else 6 for coder in list(np.unique(np.asarray(list(itertools.chain(*node_info['whos'])))))]),
                        'who':          ag,
                        'when':         when,
                        'what':         len(node_info['obs'])-1,
                        'observations': [obs for obs in node_info['obs']],
                        'ground_truth': {'situation': query_ev.situation, 'object': query_ev.obj},
                        'distance':     distance,
                        'CVR':          cvr,
                        'Kalpha':       kalpha     

                    }
            writer.writerow(info)