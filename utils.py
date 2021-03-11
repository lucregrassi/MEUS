import json
import pprint
import operator
from functools import reduce  # forward compatibility for Python 3
import matplotlib.pyplot as plt
from InformationElement import DirectObservation


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
    # avoid_duplicates = [] # list to avoid putting 2 identical direct observation objects


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
        
        # if not data_do[j] in avoid_duplicates:
        #     avoid_duplicates.append(data_do[j])
        # else:
        #     for k in range(len(avoid_duplicates)):
        #         if data_do[j]==avoid_duplicates[k]:
        #             # print("data_ih[k] before: " +str(data_ih[k]))
        #             # print("data_ih[j] before: " +str(data_ih[j]))
        #             data_ih[k].extend(data_ih[j])
        #             data_ih[j].clear()
        #     #         print("data_ih[k] after: " +str(data_ih[k]))
        #     #         print("data_ih[j] after: " +str(data_ih[j]))
        #     print("**********************************************************")
        #     print(data_do)
        #     print(data_ih)
        #     print(str(data_do[j]) + " was already in the list")
    
    # data_do = avoid_duplicates

    return data_do, data_ih


#   Preprocessing function for the incoming PUT method
# def preProcessing(json_data):
#     data_ih = []    # list of dictionaries storying the exchange of the information
#     data_do = []    # list of direct observation informations


#     # print ("json_data: " +str(json_data))
#     # print("type of json_data: " +str(type(json_data)))

#     # print("len(json_data): " + str(len(json_data)))
#     # input("check check double check")
#     i = 0
#     for j in range(len(json_data)):
#         # Retrieving the Direct Observation information
#         if not isinstance(json_data[j], dict): json_data[j] = json_data[j].asdict()
#         prev_nest = json_data[j]
#         next_nest = json_data[j].get('what')
#         data_ih.append([])
#         # while( next(iter(next_nest)) != 'event'):
#         while( not isinstance(next_nest, DirectObservation)):

#             data_ih[j].append({
#                 'a1':       prev_nest['history'][0],
#                 'a2':       prev_nest['history'][1],
#                 'where':    prev_nest['where'],
#                 'when':     prev_nest['when']
#             })
#             # updating nesting levels
#             next_nest = next_nest.asdict()
#             prev_nest = next_nest
#             next_nest = next_nest['what']

#             print("counter: "+str(i))
#             i += 1


#         # convert the dir obs object into a dictionary
#         next_nest = next_nest.asdict()
#         next_nest['event'] = {  'situation': str(next_nest['event'][0]).split(".", 1)[1],
#                                 'object': str(next_nest['event'][1]).split(".", 1)[1]
#                                 }
#         data_do.append({})
#         data_do[j]['dir_obs']   = next_nest#next_nest['event']
#         data_do[j]['when']      = prev_nest['when']
#         data_do[j]['where']     = prev_nest['where']
#         data_do[j]['who']       = prev_nest['id']


#     # print("data_do: " +str(data_do))
#     # print("data_ih: " +str(data_ih))
#     # input("check check double check")

#     return data_do, data_ih



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

    

