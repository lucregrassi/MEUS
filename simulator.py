import csv
import copy
import math
import random
import logging
import statistics
import numpy as np
import osmnx as ox
import pandas as pd
from Agent import Agent
from owlready2 import *
from read_ontology import get_cls_at_dist
from utils import NewIEtoDict, plot_agent_perf, getIndexOfTuple, ran_gen, pr_gen, latency_plot, latency_meanStddev_plot
from InformationElement import NewInformationElement, NewDirectObservation

import requests
import json
from pprint import pprint
import time

# logging.basicConfig(level=logging.INFO, filename='simulator80%.log', filemode='w')
# np.random.seed(3)

class Simulator:
    def __init__(self, n_agents=100, n_gateways=0.3, loop_distance = 20, seed=3, threshold=70, err_rate=0.25):
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
        self.same_root          = False
        self.already_told       = False


    def compute_destination(self, current_node, ag):

        # tic = time.perf_counter()
        source_nodes = []
        target_nodes = []
        # Look for all the sources and the targets of the current node
        for e in self.G.edges():
            source, target = e
            if source == current_node:
                target_nodes.append(target)
            if target == current_node:
                source_nodes.append(source)
        
        # toc = time.perf_counter()
        # print("perf:", toc-tic)
        # input()

        adj_nodes           = source_nodes + target_nodes
        distance            = 0
        destination_node    = 0

        # If there are adjacent nodes (at least a source or a target), pick one randomly as the destination
        if adj_nodes:
            inde2               = np.random.randint(0, len(adj_nodes))
            if inde2==len(adj_nodes):
                inde2 -= 1
            destination_node    = adj_nodes[inde2]

            if destination_node in target_nodes:
                edges_of_interest = self.G[current_node][destination_node]
            else:
                edges_of_interest = self.G[destination_node][current_node]
                
            for edge in edges_of_interest.values():
                distance = edge.get('length')
                # ls = compute_intermediate_dist(edge)
                if distance < 0:
                    input("distance is negative!!!")

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
                        if len(candidate.ies)>0:
                            if candidate.n != listener.n:
                                perform_exchange = False
                                # Look for common local connections
                                if any(j in candidate.local_conn for j in listener.local_conn):
                                    # print("\nCommon local connection found for agents ", candidate.n, "and", listener.n)
                                    perform_exchange = True
                                    # print("node: ", int(k))
                                # else:
                                    # print("\nNo common local connections found bewteen", candidate.n, "and", listener.n)
                                # If there is at least a common local connection or a common global connection available
                                if perform_exchange:
                                    both_global = False
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
                                                # same_root_IE_listener = copy.deepcopy(IE_listener)
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
            for n in self.G.nodes.data():
                if n[0] == previous_node:
                    n[1]['n_agents'] = int(n[1]['n_agents']) - 1
                    # If it has still not been removed from that node, delete it so that no exchange is possible
                    if str(n[0]) in self.node_state_dict:
                        if a.n in self.node_state_dict[str(n[0])]:
                            self.node_state_dict[str(n[0])].remove(a.n)

                elif n[0] == a.curr_node:
                    n[1]['n_agents'] = int(n[1]['n_agents']) + 1
                    # if this node is not yet in the dictionary, create the key-value pair
                    if not self.node_state_dict.get(str(n[0])):
                        self.node_state_dict[str(n[0])] = [a.n]
                    # if the node is already in the dictionary, append to the value the agent's id
                    else:
                        self.node_state_dict[str(n[0])].append(a.n)

                    if n[1]['situation'] != 'None':
                        flag = True
                        node_situation  = n[1]['situation']
                        node_object     = n[1]['object']

            # Add the new current node to the list of visited nodes of the person
            a.visited_nodes.append(a.curr_node)
            # The actual situation and object seen by the person depend on its trustworthiness
            if flag:
    
                a.error = np.random.normal(a.mu, a.sigma, 1)[0]

                # logging.info("B " + str(a.error))
                # logging.info(loop)


                # seen_sit = get_cls_at_dist(node_situation, a.error, a.mu, a.sigma, a.n)
                # seen_obj = get_cls_at_dist(node_object, a.error, a.mu, a.sigma, a.n)
                # seen_ev = seen_sit, seen_obj
                # if pr_gen()==1:
                chance = random.random()
                if chance<=self.err_rate:
                    distance = 2 if chance<=0.05 else 1
                    seen_sit    = get_cls_at_dist(node_situation, distance=distance)
                    seen_obj    = get_cls_at_dist(node_object, distance=distance)
                    seen_ev     = (seen_sit, seen_obj)
                else:
                    seen_ev     = (node_situation, node_object)
                # seen_ev = node_situation, node_object
                # logging.info(seen_ev)
                a.seen_events.append(seen_ev)
                # print("a.seen_events: ", a.seen_events)
                # input("hit enter")
                # Add what the person thinks to have seen to its list of information elements
                # root = NewDirectObservation(a.n, a.curr_node, loop, seen_ev, a.error)
                a.ies.append([NewInformationElement(a.n, a.curr_node, loop, NewDirectObservation(seen_ev, a.error))])


                a.error_list.append((a.error, loop))

                # conn = self.G.nodes.get(a.curr_node)['connection']
                # conn = conn.split(",")
                # conn_new = [int(i) for i in conn]

                # connection = 1 if any(j!=0 for j in conn_new) else 0

                # with open('40%.csv', 'a') as f:
                #     csv_writer = csv.DictWriter(f, fieldnames=fieldnames4)
                    
                #     info = {
                #         'id':       a.n,
                #         'sit':      node_situation,
                #         'obj':      node_object,
                #         'when':     loop,
                #         'where':    a.curr_node,
                #         'conn':     connection

                #     }
                #     csv_writer.writerow(info)


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

        # logging.info("send_info")
        conn = self.G.nodes.get(agent.curr_node)['connection']
        conn = conn.split(",")
        conn_new = [int(i) for i in conn]

        if any(j in agent.global_conn for j in conn_new) and len(agent.ies) > 0 and agent.num_info_sent < len(agent.ies):
            
            knowledge = []

            reputs  = []
            reputs2 = []
            reliabs = []

            for i in range(agent.num_info_sent, len(agent.ies)):
                copia_ie = copy.deepcopy(agent.ies[i])
                copia_ie = NewIEtoDict(copia_ie)

                n = str(copia_ie[0]['id'])

                knowledge.append(copia_ie)

                reputs.append(self.agents_dict[n].reputation)
                reputs2.append(self.agents_dict[n].reputation2)


                reliabs.append(
                    self.agents_dict[n].error_list[ getIndexOfTuple(    self.agents_dict[n].error_list, 1, copia_ie[0]['when']) ][0]
                    )

            knowledge.append({  'db_sender':        agent.n,
                                'time':             loop,
                                'sent_where':       agent.curr_node,
                                'reputations':      reputs,
                                'reputations2':     reputs2,
                                'reliabilities':    reliabs})
 
            response = requests.put(self.BASE + "IE/1", json.dumps(knowledge))
            res = response.json()


            # reputations
            for k in range(len(res['reputation'])):
                
                key = str(res['reputation'][k]['id'])

                self.agents_dict[key].reputation     = res['reputation'][k]['rep']
                self.agents_dict[key].num_info_seen  = res['reputation'][k]['times']

                self.agents_dict[key].reputation2    = res['reputation2'][k]['rep']
                self.agents_dict[key].num_info_seen2 = res['reputation2'][k]['times']

                if self.first_time:

                    self.mean_succ_rate.append(statistics.mean(self.agents_dict[i].reputation for i in self.agents_dict.keys()\
                                                        if self.agents_dict[i].num_info_seen > 0))
                    
                    self.stddev_succ_rate.append(statistics.stdev(self.agents_dict[i].reputation for i in self.agents_dict.keys()\
                                                        if self.agents_dict[i].num_info_seen > 0))
                    

                    self.mean_succ_rate2.append(statistics.mean(self.agents_dict[i].reputation2 for i in self.agents_dict.keys()\
                                                        if self.agents_dict[i].num_info_seen > 0))

                    self.stddev_succ_rate2.append(statistics.stdev(self.agents_dict[i].reputation2 for i in self.agents_dict.keys()\
                                                        if self.agents_dict[i].num_info_seen > 0))

                # if oldkey!=key and res['reputation'][k]['when'] not in self.agents_dict2[key]['when']:

                self.agents_dict2[key]['rep'].append(res['reputation'][k]['rep'])
                # self.agents_dict2[key]['rel'].append(res['reputation'][k]['rel'])
                self.agents_dict2[key]['when'].append(res['reputation'][k]['when'])
                self.agents_dict2[key]['rep2'].append(res['reputation2'][k]['rep'])

                self.first_time=True
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
                        self.latency.append(res['latency'][ind]['sent_at_loop'])


                        ind += 1

                        if self.perc_seen_ev>=self.threshold:
                            pprint(self.latency)
                            input()
                            return


            # elif loop >= len(self.events) and 'all_events_db' in res:
            #     toc_all_db = time.perf_counter()
            #     self.t_all = toc_all_db - self.tic

            if agent.num_info_sent>0 and not (len(agent.ies)-agent.num_info_sent) == (len(knowledge)-1):
                print("Houston we have a problem!")
                print("agent.num_info_sent: ", agent.num_info_sent)
                print("len(agent.ies): ", len(agent.ies))
                print("len(knowledge): ", len(knowledge)-1)
                pprint(knowledge)
                input()

            # consider only informations that have not yet been sent to the db
            prior_threshold = agent.num_info_sent
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
            if i > ag_global and not g_flag:
                
                mu, sigma = 0, 2
                g_flag = True

            err = np.random.normal(mu, sigma, 1)[0]
            # err = 0

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

                        # Add the event that the person thinks to have seen to the list
                        chance = random.random()
                        if chance<=self.err_rate:
                            distance = 2 if chance<=0.05 else 1
                            seen_situation  = get_cls_at_dist(situation, distance=distance)
                            seen_object     = get_cls_at_dist(obj, distance=distance)
                            seen_event      = (seen_situation, seen_object)
                        else:
                            seen_event = (situation, obj)

                        agent.seen_events.append(seen_event)
                        agent.ies.append([NewInformationElement(i, curr_node, 0, NewDirectObservation(seen_event, agent.error))])
                        agent.error_list.append((agent.error, 0))


            # Initialize the connections owned by the person
            if i < ag_global:
                agent.global_conn = [1, 2, 3]

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
                                        }


            # # prova del 9 code
            # if 70 <= i < 80:
            #     agent.global_conn = []
            

        # Exchange info between agents in the initial position
        self.exchange_information(0)

        old_story = 0
        count = 0
        while self.perc_seen_ev<self.threshold:
        # while self.obs_ev < 6:
            # obs_ev = 0
            print("\nIteration " + str(count))

            for key in self.agents_dict.keys():
                # Update the position of the agent
                self.update_position(self.agents_dict[key], count)

                # if key=='79' and len(self.agents_dict[key].visited_nodes) > old_story:
                #     logging.info("loop:" + str(count))
                #     logging.info(self.agents_dict[key])

                #     old_story = len(self.agents_dict[key].visited_nodes)
            
            self.exchange_information(count)

            for key in self.agents_dict.keys():
                self.send_info(self.agents_dict[key], count)

            # for counter in range(len(self.events)):
            #     if 'db_time' in self.events[counter]:
            #         obs_ev += 1

            # self.perc_seen_ev = 100*obs_ev/len(self.events)
            print(f"percentage of events seen: {self.perc_seen_ev:0.2f}%")
            count += 1
            # if count==200:
            #     break

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

        self.tic        = time.perf_counter()
        self.num_loops  = self.simulate()
        self.toc        = time.perf_counter()

        pprint(self.events)

        print("total time to get all events on the db: ", self.t_all)
        print(f"Experiment finished in {self.toc - self.tic:0.4f} seconds")



if __name__=="__main__":

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

    # with open('40%.csv', 'w') as f:
    #     csv_writer = csv.DictWriter(f, fieldnames=fieldnames4)
    #     csv_writer.writeheader()

    # with open('latency_tab_100%.csv', 'w') as f:
    #     wr = csv.DictWriter(f, fieldnames=fields2)
    #     wr.writeheader()


    simulator = Simulator(  n_agents        = 100,
                            n_gateways      = 0.5,
                            loop_distance   = 20,
                            seed            = 57,
                            threshold       = 40,
                            err_rate        = 0.35)
    simulator.run()


    with open('performances.csv', 'a') as csv_file:
        csv_writer3 = csv.DictWriter(csv_file, fieldnames=fieldnames3)

        info = {
            'time':                 simulator.toc-simulator.tic,
            'perc_of_seen_events':  simulator.perc_seen_ev
        }
        csv_writer3.writerow(info)

    
    with open('reputations.csv', 'a') as csv_file:
        csv_writer4 = csv.DictWriter(csv_file, fieldnames=fields)

        for key in simulator.agents_dict.keys():

            conf_interval = 0
            if 0 <= abs(simulator.agents_dict[key].error) < 1:
                conf_interval = 1

            elif 1 <= abs(simulator.agents_dict[key].error) < 2:
                conf_interval = 2

            else:
                conf_interval = 3


            info = {
                'id':                      simulator.agents_dict[key].n,
                'reputation':              round( simulator.agents_dict[key].reputation, 2),
                'reputation2':             round( simulator.agents_dict[key].reputation2, 2),
                'std_dev':                 simulator.agents_dict[key].sigma, 
                'number_of_seen_events':   simulator.agents_dict[key].num_info_seen
            }
            csv_writer4.writerow(info)


    rep_file = pd.read_csv('reputations.csv')
    reps = rep_file['reputation']

    # if math.floor(simulator.n_gateways*simulator.n_agents)!=100:
    #     mean_error_rate1 = statistics.mean(reps[:math.floor(simulator.n_gateways*simulator.n_agents)])
    #     mean_error_rate2 = statistics.mean(reps[math.floor(simulator.n_gateways*simulator.n_agents):])
    # else:
    #     mer = statistics.mean(reps)

    path = '/Users/mario/Desktop/Fellowship_Unige/experiments/100/Amatrice/28-06/seed' + str(simulator.seed) #+ '/Amatrice_reps_' +str(int((1-simulator.err_rate)*100)) + '%'
    # fieldn = ['lats']
    # with open(path + '/error_plot_{0}%.csv'.format(str(simulator.n_gateways*100)), 'w') as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldn)
    #     writer.writeheader()
    
    # with open(path + '/error_plot_{0}%.csv'.format(str(simulator.n_gateways*100)), 'a') as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldn)
    #     for el in simulator.latency:
    #         writer.writerow({'lats': el})


    for key in simulator.agents_dict.keys():

        simulator.agents_dict[key].ordered_reps  = list(zip(simulator.agents_dict2[key]['rep'], simulator.agents_dict2[key]['when']))
        simulator.agents_dict[key].ordered_reps2 = list(zip(simulator.agents_dict2[key]['rep2'], simulator.agents_dict2[key]['when']))
        # simulator.agents_dict[key].ordered_rels  = list(zip(simulator.agents_dict2[key]['rel'], simulator.agents_dict2[key]['when']))

        simulator.agents_dict[key].ordered_reps.sort(   key=lambda a: a[1])
        simulator.agents_dict[key].ordered_reps2.sort(  key=lambda a: a[1])
        # simulator.agents_dict[key].ordered_rels.sort(   key=lambda a: a[1])

        
        # if len(simulator.agents_dict[key].ordered_reps)>1:
        #     if math.floor(simulator.n_gateways*simulator.n_agents)!=100:
        #         if int(key) >= math.floor(simulator.n_gateways*simulator.n_agents):
        #             plot_agent_perf(simulator.agents_dict[key], key, mean_error_rate2)
        #         else:
        #             plot_agent_perf(simulator.agents_dict[key], key, mean_error_rate1)
        #     else:
        #         plot_agent_perf(simulator.agents_dict[key], key, mer)
        # if len(simulator.agents_dict[key].ordered_reps)>1:
        #     plot_agent_perf(simulator.agents_dict[key], key, path, simulator.err_rate)

    # pprint(simulator.mean_succ_rate)
    # pprint(simulator.stddev_succ_rate)
    # input()
    latency_meanStddev_plot(    simulator.mean_succ_rate,
                                simulator.stddev_succ_rate,
                                simulator.mean_succ_rate2,
                                simulator.stddev_succ_rate2,
                                simulator.err_rate,
                                path)


    input("check 3 explore_graph.py")
    response = requests.delete(simulator.BASE + "IE/1" )
    res = response.json()
    pprint(res)



    with open('experiments.csv', 'a') as csv_file:
            csv_writer2 = csv.DictWriter(csv_file, fieldnames=fieldnames1)

            info = {
                'sizeTab1':     res['size_tab1'],
                'sizeTab2':     res['size_tab2'],
                'latency':      statistics.mean(simulator.latency),
                'num_loops':    simulator.num_loops
            }
            csv_writer2.writerow(info)