import csv
import copy
import math
import json
import time

import random
import logging
import requests
import statistics
from os import path

import numpy as np
import osmnx as ox
import pandas as pd
from owlready2 import *

from Agent import Agent
from pprint import pprint
import matplotlib.pyplot as plt
from read_ontology import get_cls_at_dist
from InformationElement import NewInformationElement, NewDirectObservation
from utils import NewIEtoDict, plot_agent_perf, getIndexOfTuple, ran_gen, pr_gen, latency_plot, latency_meanStddev_plot



class Simulator:
    def __init__(self, n_agents=100, n_gateways=0.3, loop_distance=20, seed=3, threshold=70, err_rate=0.25):
        self.n_agents           = n_agents
        self.n_gateways         = n_gateways
        self.perc_seen_ev       = 0
        self.loop_distance      = loop_distance
        self.agents_dict        = {}
        self.agents_dict2       = {}
        self.node_state_dict    = {}
        self.events             = []
        self.G                  = ox.load_graphml('graph/graph.graphml')
        self.tic                = 0
        self.toc                = 0
        self.t_all              = 0
        self.BASE               = "http://127.0.0.1:5000/"
        self.seed               = seed
        self.num_loops          = 0
        self.threshold          = threshold
        self.onto               = get_ontology("ontology/MEUS.owl")
        self.obs_ev             = 0
        self.latency            = []
        self.err_rate           = err_rate
        self.mean_succ_rate     = []
        self.mean_succ_rate2    = []
        self.stddev_succ_rate   = []
        self.stddev_succ_rate2  = []
        self.first_time         = False
        self.similarity_err     = []
        self.loop_duration      = []
        self.mean_loop_duration = []


    def compute_destination(self, current_node, ag):

        # if len([n for n in self.G.neighbors(current_node)])==0:
        #     print([n for n in self.G.neighbors(current_node)])
        source_nodes = []
        target_nodes = []
        # Look for all the sources and the targets of the current node
        for e in self.G.edges():
            source, target = e
            if source == current_node:
                target_nodes.append(target)
            if target == current_node:
                source_nodes.append(source)


        adj_nodes           = source_nodes + target_nodes
            # print(adj_nodes)
            # input()

        # destination_node    = int(np.random.choice([n for n in self.G.neighbors(current_node)]))
        destination_node    = int(np.random.choice(adj_nodes))
        if destination_node in target_nodes:
                edges_of_interest = self.G[current_node][destination_node]
        else:
            edges_of_interest = self.G[destination_node][current_node]
            
        for edge in edges_of_interest.values():
            distance = edge.get('length')
        # distance            = self.G[current_node][destination_node][0]['length']

        return destination_node, distance


    def exchange_information(self, loop):
        delete = []
        for k in self.node_state_dict.keys():
            # If there is more than one agent in a node, they should exchange their info
            if len(self.node_state_dict[k]) > 1:
                delete.append(k)
                for agent_id in self.node_state_dict[k]:
                    listener = self.agents_dict[str(agent_id)]
                    for ag_id in self.node_state_dict[k]:
                        # If the teller has a different id (is not the listener), and if they both have
                        candidate = self.agents_dict[str(ag_id)]
                        if candidate.n != listener.n and len(candidate.ies)>0:
                            # Look for common local connections
                            perform_exchange = True if any(j in candidate.local_conn for j in listener.local_conn) else False
                            # If there is at least a common local connection or a common global connection available
                            if perform_exchange:
                                teller = candidate
                                listener.met_agents.append(teller.n)
                                listener.met_in_node.append(int(k))
                                listener.met_in_loop.append(loop)

                                # Loop through all Information Elements of the teller
                                for IE_teller in teller.ies:
                                    same_root = False
                                    already_told = False
                                    # print("teller: ", IE_teller[0],", ",IE_teller[1:])
                                    for i, lis_ie in enumerate(listener.ies):
                                        # If the IEs have the same root (can happen only once)
                                        if IE_teller[0] == lis_ie[0]:
                                            same_root = True
                                            index = i
                                            # For each quadrupla in the IE
                                            for quadrupla in IE_teller[1:]:
                                                # If the listener is not a teller in a tuple of the IE,
                                                # or the teller has not previously told the information to the listener
                                                if quadrupla[0]==listener.n:
                                                    already_told = True
                                                    break
                                            for tup in lis_ie[1:]:
                                                if (tup[0]==teller.n and tup[1]==listener.n):
                                                    already_told = True
                                                    break

                                    if not already_told:
                                        if same_root:
                                            if len(IE_teller[1:]) > 0:

                                                target_extend = []
                                                target_extend.append((teller.n, listener.n, int(k), loop))
                                                target_extend.extend(elem for elem in IE_teller[1:] if elem not in listener.ies[index])

                                                # communicating the information to the listener
                                                listener.ies[index].extend(target_extend)
                                            else:
                                                listener.ies[index].append((teller.n, listener.n, int(k), loop))
                                        else:
                                            # Append the new IE to the listener (making a deepcopy of the IE of the teller)
                                            listener.ies.append(copy.deepcopy(IE_teller))
                                            listener.ies[-1].append((teller.n, listener.n, int(k), loop))

        # Avoid that they can meet again once they exchange their info and they are still in the same node
        for k in delete:
            del self.node_state_dict[k]


    def update_position(self, a, loop): 

        if not a.moving:
            # Arrived to destination node
            previous_node               = a.curr_node
            a.curr_node                 = a.dest_node
            destination_node, distance  = self.compute_destination(a.dest_node, a.n)
            a.dest_node                 = destination_node
            a.distance                  = distance
            # a.path = path
            a.moving = True
            a.road = 0


            node_situation = []
            node_object = []
            flag = False
            # Update the counters in the nodes and acquire the situation and the object in the new current node
            self.G.nodes[previous_node]['n_agents']  = int(self.G.nodes[previous_node]['n_agents']) - 1
            self.G.nodes[a.curr_node]['n_agents']    = int(self.G.nodes[a.curr_node]['n_agents'])   + 1

            if (str(previous_node)) in self.node_state_dict and a.n in self.node_state_dict[str(previous_node)]:
                self.node_state_dict[str(previous_node)].remove(a.n)

            if not self.node_state_dict.get(str(a.curr_node)):
                self.node_state_dict[str(a.curr_node)] = [a.n]
            else:
                self.node_state_dict[str(a.curr_node)].append(a.n)

            if self.G.nodes[a.curr_node]['situation'] != 'None':
                flag = True
                node_situation  = self.G.nodes[a.curr_node]['situation']
                node_object     = self.G.nodes[a.curr_node]['object']


            # Add the new current node to the list of visited nodes of the person
            a.visited_nodes.append(a.curr_node)
            # The actual situation and object seen by the person depend on its trustworthiness
            if flag:
    
                # agents can have an error rate in the interval [0.5, 1]
                a.error = round(np.random.random(), 2)

                if a.error<self.err_rate:
                    seen_sit    = get_cls_at_dist(node_situation, self.err_rate, distance=a.error)
                    seen_obj    = get_cls_at_dist(node_object, self.err_rate, distance=a.error)
                    seen_ev     = (seen_sit, seen_obj)
                else:
                    seen_ev     = (node_situation, node_object)

                a.seen_events.append(seen_ev)
                a.ies.append([NewInformationElement(a.n, a.curr_node, loop, NewDirectObservation(seen_ev, a.error))])
                a.error_list.append((a.error, loop))
                # a.rating_list.append((a.rating, loop))

        else:
            # If the person is moving, check if it has reached the destination
            if a.distance > 0:
                # If it has not reached the destination, move of the defined distance
                a.distance  -= self.loop_distance
                a.road      += self.loop_distance 

                # geolocalise_me(a)
            else:
                # If the distance is 0 or negative it means that the destination has been reached
                a.moving = False


    def send_info(self, agent, loop):

        conn = self.G.nodes.get(agent.curr_node)['connection']
        conn = conn.split(",")
        conn_new = [int(i) for i in conn]

        if any(j in agent.global_conn for j in conn_new) and len(agent.ies) > 0 and agent.num_info_sent < len(agent.ies):
            
            knowledge = []

            # reputs  = []
            # reputs2 = []
            # reliabs = []
            # ratings = []

            # for i in range(agent.num_info_sent, len(agent.ies)):
            #     ie = copy.deepcopy(agent.ies[i])
            #     ie = NewIEtoDict(ie)

            #     n = str(ie[0]['id'])

            #     knowledge.append(ie)

            knowledge = [NewIEtoDict(copy.deepcopy(agent.ies[i])) for i in range(agent.num_info_sent, len(agent.ies))]
                # reputs.append(self.agents_dict[n].reputation)
                # reputs2.append(self.agents_dict[n].reputation2)


                # reliabs.append(
                #     self.agents_dict[n].error_list[ getIndexOfTuple(    self.agents_dict[n].error_list, 1, ie[0]['when']) ][0]
                #     )

                # ratings.append(
                #     self.agents_dict[n].rating_list[ getIndexOfTuple(    self.agents_dict[n].rating_list, 1, ie[0]['when']) ][0]
                # )

            # knowledge.append({  'db_sender':        agent.n,
            #                     'time':             loop,
            #                     'sent_where':       agent.curr_node,
            #                     'reputations':      reputs,
            #                     'reputations2':     reputs2,
            #                     'reliabilities':    reliabs})
            knowledge.append({  'db_sender':        agent.n,
                                'time':             loop,
                                'sent_where':       agent.curr_node})
 
            response = requests.put(self.BASE + "IE/1", json.dumps(knowledge))
            res = response.json()

            # '''weights update'''
            # for a in res['weights'].items():
            #     self.agents_dict[str(a[0])].weight = a[1]


            # ''' Reputations '''
        
            # for l, rep in enumerate(res['reputation']):

            #     key = str(rep['id'])

            #     self.agents_dict[key].reputation     = rep['rep']
            #     self.agents_dict[key].reputations.append(self.agents_dict[key].reputation)
            #     self.agents_dict[key].num_info_seen  = rep['times']
            #     self.agents_dict2[key]['rep'].append(rep['rep'])
            #     self.agents_dict2[key]['when'].append(rep['when'])

            #     if self.first_time:

            #         self.mean_succ_rate.append(statistics.mean(self.agents_dict[i].reputation for i in self.agents_dict.keys()\
            #                                                     if self.agents_dict[i].num_info_seen > 0))
                    
            #         self.stddev_succ_rate.append(statistics.stdev(self.agents_dict[i].reputation for i in self.agents_dict.keys()\
            #                                                     if self.agents_dict[i].num_info_seen > 0))

            #     self.first_time=True
            # self.first_time=False
            
            # for k, rep2 in enumerate(res['reputation2']):
                
            #     key = str(rep2['id'])

            #     if 'times' in res['reputation2'][k]:

            #         self.agents_dict[key].reputation2    = rep2['rep']
            #         self.agents_dict[key].reputations2.append(self.agents_dict[key].reputation2 )
            #         self.agents_dict[key].num_info_seen2 = rep2['times']
            #         self.agents_dict2[key]['rep2'].append(rep2['rep'])
            #         self.agents_dict2[key]['when2'].append(rep2['when'])

            #     else:
            #         key = str(rep2['id'])
            #         self.agents_dict[key].reputation2   = rep2['rep']
            #         self.agents_dict[key].reputations2.append(self.agents_dict[key].reputation2 )
            #         self.agents_dict2[key]['rep2'].append(rep2['rep'])
            #         self.agents_dict2[key]['when2'].append(loop)

            #     if self.first_time:

            #         self.mean_succ_rate2.append(statistics.mean(self.agents_dict[i].reputation2 for i in self.agents_dict.keys()\
            #                                                     if self.agents_dict[i].num_info_seen > 0))

            #         self.stddev_succ_rate2.append(statistics.stdev(self.agents_dict[i].reputation2 for i in self.agents_dict.keys()\
            #                                                     if self.agents_dict[i].num_info_seen > 0))

            #     self.first_time=True

            # self.similarity_err.append(statistics.mean( abs(self.agents_dict[j].reputation - self.agents_dict[j].reputation2) for j in self.agents_dict.keys()\
            #                                                     if self.agents_dict[j].num_info_seen > 0))

            # percentage of events seen
            if 'events' in res:
                ind = 0
                for i, ev in enumerate(res['events']):

                    # checking if its the first time the observation has been made
                    if ev['first_time']==1 and 'db_time' not in self.events[i]:
                    
                        self.events[i]  = ev

                        toc_db  = time.perf_counter()
                        t       = toc_db - self.tic
                        self.events[i]['db_time'] = t

                        self.obs_ev += 1
                        self.perc_seen_ev = 100*self.obs_ev/len(self.events)

                        # self.latency.append(res['latency2'][indice]['lat'])
                        if ind > len(res['latency']):
                            pprint(res['latency'])
                            print(ind)
                            input()
                        self.latency.append(res['latency'][ind]['sent_at_loop'])

                        ind += 1

                        if self.perc_seen_ev>=self.threshold:
                            return


            # elif loop >= len(self.events) and 'all_events_db' in res:
            #     toc_all_db = time.perf_counter()
            #     self.t_all = toc_all_db - self.tic

            # if agent.num_info_sent>0 and not (len(agent.ies)-agent.num_info_sent) == (len(knowledge)-1):
            #     print("Houston we have a problem!")
            #     print("agent.num_info_sent: ", agent.num_info_sent)
            #     print("len(agent.ies): ", len(agent.ies))
            #     print("len(knowledge): ", len(knowledge)-1)
            #     pprint(knowledge)
            #     input()

            # consider only informations that have not yet been sent to the db
            prior_threshold     = agent.num_info_sent
            agent.num_info_sent += (len(agent.ies) - prior_threshold)


    def simulate(self):

        ag_global = math.floor(self.n_gateways*self.n_agents)

        mu, sigma = 0, 1

        l = [n[0] for n in self.G.nodes.data()]

        g_flag = False
        for i in range(self.n_agents):

            # curr_node = random.choice(list(n[0] for n in self.G.nodes.data()))
            # inde = np.random.randint(0, len(l)-1)
            curr_node = l[np.random.randint(0, len(l)-1)]

            situation = {}
            obj = []

            dest_node, dist = self.compute_destination(curr_node, None)

            # Instantiate the Person class passing the arguments
            # if i > ag_global and not g_flag:
                
            #     mu, sigma = 0, 2
            #     g_flag = True

            # err = np.random.normal(mu, sigma, 1)[0]
            err = np.random.random()

            agent = Agent(i, curr_node, dest_node, dist, err) #if i!= 3 else Agent(i, curr_node, dest_node, dist, 0)
            
            agent.mu    = mu
            agent.sigma = sigma

            agent.visited_nodes.append(curr_node)

            for elem in self.G.nodes(data=True):
                if elem[0] == curr_node:
                    # Increment the number of people in that node
                    elem[1]['n_agents'] = int(elem[1]['n_agents']) + 1
                    # Add person id to the node
                    if not self.node_state_dict.get(str(curr_node)):
                        self.node_state_dict[str(curr_node)] = [i]
                    else:
                        self.node_state_dict[str(curr_node)].append(i)

                    if elem[1]['situation'] != 'None':
                        situation = elem[1]['situation']
                        obj = elem[1]['object']

                        agent.error = round(np.random.random(), 2)

                        if agent.error<self.err_rate:
                            seen_sit    = get_cls_at_dist(situation, self.err_rate, distance=agent.error)
                            seen_obj    = get_cls_at_dist(obj, self.err_rate, distance=agent.error)
                            seen_ev     = (seen_sit, seen_obj)
                        else:
                            seen_ev = (situation, obj)

                        agent.seen_events.append(seen_ev)

                        agent.ies.append([NewInformationElement(i, curr_node, 0, NewDirectObservation(seen_ev, agent.error))])
                        agent.error_list.append((agent.error, 0))
                        # agent.rating_list.append((agent.rating, 0))


            # Initialize the connections owned by the person
            if i < ag_global:
                agent.global_conn   = [1, 2, 3]
                agent.weight        = 6

            # agent.global_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
            # Initialize array of local connections, choosing randomly, removing duplicates
            agent.local_conn = [1, 2, 3]
            # agent.local_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
            self.agents_dict[str(i)] = agent

            # initial reputation and error of each agent
            self.agents_dict2[str(i)] = {   'rep':      [agent.reputation],
                                            'rep2':     [agent.reputation2],
                                            'rel':      [agent.error],
                                            'when':     [0],
                                            'when2':    [0]
                                        }



        # Exchange info between agents in the initial position
        self.exchange_information(0)

        old_story = 0
        count = 0
        while self.perc_seen_ev<self.threshold:
        # while count < 1000:
            start_time = time.time()
        # while self.obs_ev < 6:
            # obs_ev = 0
            print("\nIteration " + str(count))

            for key in self.agents_dict.keys():
                # Update the position of the agent
                # for ie in self.agents_dict[key].ies:
                #     print(ie[0], ", ", ie[1:] )
                    # input()
                self.update_position(self.agents_dict[key], count)
            
            self.exchange_information(count)

            for key in self.agents_dict.keys():
                self.send_info(self.agents_dict[key], count)

            print(f"percentage of events seen: {self.perc_seen_ev:0.2f}%")
            count += 1

            self.loop_duration.append(time.time()-start_time)

            if count>1:
                self.mean_loop_duration.append(statistics.mean(self.loop_duration))

        return count


    def run(self):

        self.onto.load()
        np.random.seed(self.seed)

        # collecting events in the environment
        for node in self.G.nodes(data=True):
            #     print(node)
            # input("checking nodes")
            if node[1]['situation'] != 'None':

                self.events.append({
                    'situation':    node[1]['situation'],
                    'object':       node[1]['object'],
                    'where':        node[0],
                    'mistaken':     {'times': 0, 'difference': []},
                    'correct':      0,
                    'first_time':   0
                })

        inf = {'events': self.events, 'n_agents': self.n_agents}

        response = requests.put(self.BASE + "/IE/events", json.dumps(inf))

        fieldnames1 = ["sizeTab1", "sizeTab2", "latency", "num_loops"]
        fieldnames2 = ["sizeTab1", "sizeTab2"]
        fieldnames3 = ["time", "perc_of_seen_events"]
        fields = ["id", "reputation", "reputation2", "std_dev", "number_of_seen_events"]
        fields2  = ['sender', 'sit', 'obj', 'when', 'where', 'who', 'sent_at_loop', 'lat']

        fieldnames4 = ["id", "sit", "obj", "when", "where", "conn"]

        with open('experiments.csv', 'w') as csv_file:
            csv_writer1 = csv.DictWriter(csv_file, fieldnames=fieldnames1)
            csv_writer1.writeheader()


        with open('performances.csv', 'w') as csv_file:
            csv_writer3 = csv.DictWriter(csv_file, fieldnames=fieldnames3)
            csv_writer3.writeheader()

        with open('reputations.csv', 'w') as csv_file:
            csv_writer4 = csv.DictWriter(csv_file, fieldnames=fields)
            csv_writer4.writeheader()

        
        ''' Running the simulation '''
        self.tic        = time.perf_counter()
        self.num_loops  = self.simulate()
        self.toc        = time.perf_counter()

        pprint(self.events)

        print("total time to get all events on the db: ", self.t_all)
        print(f"Experiment finished in {self.toc - self.tic:0.4f} seconds")


        with open('performances.csv', 'a') as csv_file:
            csv_writer3 = csv.DictWriter(csv_file, fieldnames=fieldnames3)

            info = {
                'time':                 self.toc-self.tic,
                'perc_of_seen_events':  self.perc_seen_ev
            }
            csv_writer3.writerow(info)

    
        # with open('reputations.csv', 'a') as csv_file:
        #     csv_writer4 = csv.DictWriter(csv_file, fieldnames=fields)

        #     for key in self.agents_dict.keys():

        #         conf_interval = 0
        #         if 0 <= abs(self.agents_dict[key].error) < 1:
        #             conf_interval = 1

        #         elif 1 <= abs(self.agents_dict[key].error) < 2:
        #             conf_interval = 2

        #         else:
        #             conf_interval = 3


        #         info = {
        #             'id':                      self.agents_dict[key].n,
        #             'reputation':              round( self.agents_dict[key].reputation, 2),
        #             'reputation2':             round( self.agents_dict[key].reputation2, 2),
        #             'std_dev':                 self.agents_dict[key].sigma, 
        #             'number_of_seen_events':   self.agents_dict[key].num_info_seen
        #         }
        #         csv_writer4.writerow(info)



        # pat = '/Users/mario/Desktop/Fellowship_Unige/experiments/100/Amatrice/28-06/seed' + str(simulator.seed) + "/method1" #+ '/Amatrice_reps_' +str(int((1-simulator.err_rate)*100)) + '%'
        # # fieldn = ['lats']
        # # with open(path + '/error_plot_{0}%.csv'.format(str(simulator.n_gateways*100)), 'w') as f:
        # #     writer = csv.DictWriter(f, fieldnames=fieldn)
        # #     writer.writeheader()
        
        # # with open(path + '/error_plot_{0}%.csv'.format(str(simulator.n_gateways*100)), 'a') as f:
        # #     writer = csv.DictWriter(f, fieldnames=fieldn)
        # #     for el in simulator.latency:
        # #         writer.writerow({'lats': el})

        # fielde = ['error_rate']
        # for key in self.agents_dict.keys():
        #     if self.agents_dict[key].num_info_seen > 0:
        #         with open(pat + '/err_rate/{0}.csv'.format(key), 'w') as f:
        #             writer = csv.DictWriter(f, fieldnames=fielde)
        #             writer.writeheader()
                
        #         with open(pat + '/err_rate/{0}.csv'.format(key), 'a') as f:
        #             writer = csv.DictWriter(f, fieldnames=fielde)
        #             for el in self.agents_dict[key].reputations:
        #                 writer.writerow({ 'error_rate':    el})


        # fieldn = ['reps']
        # for key in self.agents_dict.keys():
        #     if self.agents_dict[key].num_info_seen > 0:
        #         with open(pat + '/rep/{0}.csv'.format(key), 'w') as f:
        #             writer = csv.DictWriter(f, fieldnames=fieldn)
        #             writer.writeheader()
                
        #         with open(pat + '/rep/{0}.csv'.format(key), 'a') as f:
        #             writer = csv.DictWriter(f, fieldnames=fieldn)
        #             for el in self.agents_dict[key].reputations2:
        #                 writer.writerow({ 'reps':    el})


        # for key in self.agents_dict.keys():


        #     if len(self.agents_dict2[key]['rep2'])!=len(self.agents_dict2[key]['when2']):
        #         pprint(self.agents_dict2[key]['rep2'])
        #         pprint(self.agents_dict2[key]['when2'])
        #         print(len(self.agents_dict2[key]['rep2']))
        #         print(len(self.agents_dict2[key]['when2']))
        #         input("rep2")

        #     self.agents_dict[key].ordered_reps  = list(zip(self.agents_dict2[key]['rep'], self.agents_dict2[key]['when']))
        #     self.agents_dict[key].ordered_reps2 = list(zip(self.agents_dict2[key]['rep2'], self.agents_dict2[key]['when2']))

        #     self.agents_dict[key].ordered_reps.sort(   key=lambda a: a[1])
        #     self.agents_dict[key].ordered_reps2.sort(  key=lambda a: a[1])

        #     if len(self.agents_dict[key].ordered_reps)>1:
        #         plot_agent_perf(self.agents_dict[key], key, pat, self.err_rate)



        # latency_meanStddev_plot(    self.mean_succ_rate,
        #                             self.stddev_succ_rate,
        #                             self.mean_succ_rate2,
        #                             self.stddev_succ_rate2,
        #                             self.err_rate,
        #                             pat)

        pat = '/Users/mario/Desktop/Fellowship_Unige/MEUS/'


        plt.style.use('seaborn-whitegrid')
        # plt.figure(500)
        plt.plot(self.mean_loop_duration, label='loop duration', c='b')
        
        plt.legend(loc='upper left')
        plt.ylabel('duration')
        plt.xlabel('# of loops')
        plt.tight_layout()
        plt.savefig(path.join(pat, 'loop_duration.svg'))

        # print(self.similarity_err)

        input("check 3 explore_graph.py")
        response = requests.delete(simulator.BASE + "IE/1" )
        res = response.json()
        pprint(res)



        # with open('experiments.csv', 'a') as csv_file:
        #         csv_writer2 = csv.DictWriter(csv_file, fieldnames=fieldnames1)

        #         info = {
        #             'sizeTab1':     res['size_tab1'],
        #             'sizeTab2':     res['size_tab2'],
        #             'latency':      statistics.mean(self.latency),
        #             'num_loops':    self.num_loops
        #         }
        #         csv_writer2.writerow(info)


if __name__=="__main__":


    simulator = Simulator(  n_agents        = 100,
                            n_gateways      = 0.5,
                            loop_distance   = 20,
                            seed            = 57,
                            threshold       = 50,
                            err_rate        = 0.3)
    simulator.run()
