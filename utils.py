import math
import json
import pprint
import operator
from functools import reduce  # forward compatibility for Python 3
import matplotlib.pyplot as plt
import numpy as np
from owlready2 import *
from os import path



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

    return data_do, data_ih, json_data[-1]['reputations'], json_data[-1]['reputations2'], json_data[-1]['reliabilities']


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

    # if type(lis[0]['what']['event'][0])==owlready2.entity.ThingClass:

    lis[0]['what'] = { 'situation':    str(lis[0]['what']['event'][0]).split(".", 1)[1],
                        'object':      str(lis[0]['what']['event'][1]).split(".", 1)[1]
                        }
    # else:
        # lis[0]['what'] = { 'situation':    str(lis[0]['what']['event'][0]),
        #                     'object':      str(lis[0]['what']['event'][1])
        #                     }

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
    

def plot_agent_perf(agent, key, rep):

    plt.style.use('seaborn-whitegrid')

    outpath = "/Users/mario/Desktop/exp10June/"

    plt.figure(key)

    plt.plot([t[1] for t in agent.ordered_reps], [t[0] for t in agent.ordered_reps], marker='*', c='b', label='rep', linewidth=1.1)
    plt.plot([t[1] for t in agent.ordered_reps2], [t[0] for t in agent.ordered_reps2], marker='*', c='tab:orange', label='rep2', linewidth=1.1)
    plt.plot([t[1] for t in agent.ordered_rels], [t[0] for t in agent.ordered_rels], marker='*', c='k', label='rel', linewidth=.5)
    # specifying horizontal line type
    plt.axhline(y = rep, color = 'r', linestyle = '-', linewidth=.4)


    plt.legend(loc='upper left')
    plt.ylabel('reps and rels')
    plt.xlabel('when')

    plt.tight_layout()
    plt.savefig(path.join(outpath,"agent_{0}.png".format(int(key))))
    # plt.show()


# Stops iterating through the list as soon as it finds the value
def getIndexOfTuple(l, index, value):
    for pos,t in enumerate(l):
        if t[index] == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")
    






