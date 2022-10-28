import csv
import copy
import math
import json
import shutil
import logging
import requests
import statistics
import numpy as np
import osmnx as ox
from owlready2 import *
from glob import glob
from Agent import Agent
from pprint import pprint
from ontology_utils import get_cls_at_dist
from InformationElement import NewInformationElement, NewDirectObservation
from utils import NewIEtoDict, getIndexOfTuple
from scipy.stats import halfnorm

logging.basicConfig(filename="logfile.log",
                    level=logging.DEBUG)


class Simulator:
    def __init__(self, num_exp=0, n_agents=1000, gateway_ratio=0.15, loop_distance=100, seed=69, threshold=30, std_dev=1,
                 std_dev_gateway=0.2, store_latency=False, path=os.path.abspath(os.getcwd()), radius=2, th=0,
                 param='std_dev'):
        self.n_agents = n_agents
        self.gateway_ratio = gateway_ratio
        self.perc_seen_ev = 0
        self.loop_distance = loop_distance
        self.agents_dict = {}
        self.node_state_dict = {}
        self.events = []
        self.tic = 0
        self.toc = 0
        self.t_all = 0
        self.BASE = "http://127.0.0.1:5000/"
        self.seed = seed
        self.num_loops = 0
        self.threshold = threshold
        self.onto = get_ontology("ontology/MEUS.owl")
        self.obs_ev = 0
        self.sent_at_loop = []
        self.dir_obs_latency = []
        self.std_dev = std_dev
        self.std_dev_gateway = std_dev_gateway
        self.mean_succ_rate = []
        self.stddev_succ_rate = []
        self.first_time = False
        self.similarity_err = []
        self.loop_duration = []
        self.mean_loop_duration = []
        self.store_latency = store_latency
        self.path = path
        self.radius = radius
        self.th = th
        self.param = param
        self.num_exp = num_exp
        self.G = None

    def compute_destination(self, current_node):
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

        adj_nodes = source_nodes + target_nodes
        # destination_node    = int(np.random.choice([n for n in self.G.neighbors(current_node)]))
        destination_node = int(np.random.choice(adj_nodes))
        if destination_node in target_nodes:
            edges_of_interest = self.G[current_node][destination_node]
        else:
            edges_of_interest = self.G[destination_node][current_node]
        distance = 0
        for edge in edges_of_interest.values():
            distance = edge.get('length')
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
                        if candidate.n != listener.n and len(candidate.ies) > 0:
                            # Look for common local connections
                            perform_exchange = True if any(
                                j in candidate.local_conn for j in listener.local_conn) else False
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
                                                if quadrupla[0] == listener.n:
                                                    already_told = True
                                                    break
                                            for tup in lis_ie[1:]:
                                                if tup[0] == teller.n and tup[1] == listener.n:
                                                    already_told = True
                                                    break
                                    if not already_told:
                                        if same_root:
                                            if len(IE_teller[1:]) > 0:
                                                target_extend = [(teller.n, listener.n, int(k), loop)]
                                                target_extend.extend(
                                                    elem for elem in IE_teller[1:] if elem not in listener.ies[index])

                                                # communicating the information to the listener
                                                listener.ies[index].extend(target_extend)
                                            else:
                                                listener.ies[index].append((teller.n, listener.n, int(k), loop))
                                        else:
                                            # Append the new IE to the listener (making a deepcopy of the IE of the teller)
                                            listener.ies.append(copy.deepcopy(IE_teller))
                                            listener.ies[-1].append((teller.n, listener.n, int(k), loop))

        # Avoid that they can meet again once they exchange their info, and they are still in the same node
        for k in delete:
            del self.node_state_dict[k]

    def update_position(self, a, loop):
        if not a.moving:
            # Arrived to destination node
            previous_node = a.curr_node
            a.curr_node = a.dest_node
            destination_node, distance = self.compute_destination(a.dest_node)
            a.dest_node = destination_node
            a.distance = distance
            a.moving = True
            a.road = 0

            node_situation = []
            node_object = []
            flag = False
            # Update the counters in the nodes and acquire the situation and the object in the new current node
            self.G.nodes[previous_node]['n_agents'] = int(self.G.nodes[previous_node]['n_agents']) - 1
            self.G.nodes[a.curr_node]['n_agents'] = int(self.G.nodes[a.curr_node]['n_agents']) + 1

            if (str(previous_node)) in self.node_state_dict and a.n in self.node_state_dict[str(previous_node)]:
                self.node_state_dict[str(previous_node)].remove(a.n)

            if not self.node_state_dict.get(str(a.curr_node)):
                self.node_state_dict[str(a.curr_node)] = [a.n]
            else:
                self.node_state_dict[str(a.curr_node)].append(a.n)

            if self.G.nodes[a.curr_node]['situation'] != 'None':
                flag = True
                node_situation = self.G.nodes[a.curr_node]['situation']
                node_object = self.G.nodes[a.curr_node]['object']

            # Add the new current node to the list of visited nodes of the person
            a.visited_nodes.append(a.curr_node)
            # The actual situation and object seen by the person depend on its trustworthiness
            if flag:
                seen_sit = get_cls_at_dist(node_situation, distance=a.error)
                seen_obj = get_cls_at_dist(node_object, distance=a.error)
                seen_ev = (seen_sit, seen_obj)

                a.seen_events.append(seen_ev)
                a.ies.append([NewInformationElement(a.n, a.curr_node, loop, NewDirectObservation(seen_ev, a.error))])
                if a.n < self.n_agents * self.gateway_ratio:
                    a.error_list.append((self.std_dev_gateway, loop))
                else:
                    a.error_list.append((self.std_dev, loop))
                a.err_distances.append((a.error, loop))

        else:
            # If the person is moving, check if it has reached the destination
            if a.distance > 0:
                # If it has not reached the destination, move of the defined distance
                a.distance -= self.loop_distance
                a.road += self.loop_distance
            else:
                # If the distance is 0 or negative it means that the destination has been reached
                a.moving = False

    def send_info(self, agent, loop):
        conn = self.G.nodes.get(agent.curr_node)['connection']
        conn = conn.split(",")
        conn_new = [int(i) for i in conn]
        if any(j in agent.global_conn for j in conn_new) and len(agent.ies) > 0 and agent.num_info_sent < len(
                agent.ies):
            knowledge = [NewIEtoDict(copy.deepcopy(agent.ies[i])) for i in range(agent.num_info_sent, len(agent.ies))]
            ns = [NewIEtoDict(copy.deepcopy(agent.ies[i]))[0] for i in range(agent.num_info_sent, len(agent.ies))]
            distances = [self.agents_dict[str(n['id'])].err_distances[
                             getIndexOfTuple(self.agents_dict[str(n['id'])].err_distances, 1, n['when'])][0]
                         for n in ns]
            knowledge.append({'db_sender': agent.n,
                              'distances': distances,
                              'time': loop,
                              'sent_where': agent.curr_node})
            response = requests.put(self.BASE + "IE/1", json.dumps(knowledge))
            res = response.json()

            try:
                print("Latency vector", res['latency'])
                for lat in res['latency']:
                    print("Latency:", lat['sent_at_loop'] - lat['when'])
                    self.dir_obs_latency.append(lat['sent_at_loop'] - lat['when'])
            except KeyError as er:
                print(er)

            # print(res)
            # Percentage of seen events
            if 'events' in res:
                ind = 0
                for i, ev in enumerate(res['events']):
                    # checking if it's the first time the observation has been made

                    if ev['first_time'] == 1 and 'db_time' not in self.events[i]:
                        self.events[i] = ev
                        toc_db = time.perf_counter()
                        t = toc_db - self.tic
                        self.events[i]['db_time'] = t
                        self.obs_ev += 1
                        # Percentage of seen events
                        self.perc_seen_ev = 100 * self.obs_ev / len(self.events)
                        self.sent_at_loop.append(res['latency'][ind]['sent_at_loop'])
                        ind += 1
            if self.perc_seen_ev >= self.threshold:
                return
            # consider only information that have not yet been sent to the db
            prior_threshold = agent.num_info_sent
            agent.num_info_sent += (len(agent.ies) - prior_threshold)

    def simulate(self):
        n_gateway_agents = math.floor(self.gateway_ratio * self.n_agents)
        mu, sigma = 0, 1
        l = [n[0] for n in self.G.nodes.data()]

        normal_agents = self.n_agents-n_gateway_agents
        # Generate float values distributed normally, centered in 0 and a certain standard deviation
        rv = halfnorm.rvs(loc=0, scale=self.std_dev, size=normal_agents)
        distances = []
        for elem in rv:
            if math.floor(elem) > 3:
                distances.append(3)
            else:
                distances.append(math.floor(elem))

        rv = halfnorm.rvs(loc=0, scale=self.std_dev_gateway, size=n_gateway_agents)
        distances_gateway = []
        for elem in rv:
            if math.floor(elem) > 3:
                distances_gateway.append(3)
            else:
                distances_gateway.append(math.floor(elem))

        normal_agent_weight = math.ceil(6/(self.std_dev/0.5))
        gateway_agent_weight = math.ceil(6/(self.std_dev_gateway/0.5))
        requests.post(self.BASE + "/IE", data=json.dumps({"normal_agent_weight": normal_agent_weight,
                                                          "gateway_agent_weight": gateway_agent_weight}))

        # Initialize agents
        for i in range(self.n_agents):
            curr_node = l[np.random.randint(0, len(l) - 1)]
            dest_node, dist = self.compute_destination(curr_node)

            # The error of an agent is initialized to zero
            agent = Agent(i, curr_node, dest_node, dist, mu=mu, sigma=sigma)
            # Initialize the connections owned by the person
            if i < n_gateway_agents:
                agent.global_conn = [1, 2, 3]
                agent.error = distances_gateway[i]
            else:
                agent.error = distances[i-n_gateway_agents]
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

                        seen_sit = get_cls_at_dist(situation, distance=agent.error)
                        seen_obj = get_cls_at_dist(obj, distance=agent.error)
                        seen_ev = (seen_sit, seen_obj)

                        agent.seen_events.append(seen_ev)

                        agent.ies.append(
                            [NewInformationElement(i, curr_node, 0, NewDirectObservation(seen_ev, agent.error))])
                        if i < n_gateway_agents:
                            agent.error_list.append((self.std_dev_gateway, 0))
                        else:
                            agent.error_list.append((self.std_dev, 0))
                        agent.err_distances.append((agent.error, 0))

            # Initialize array of local connections, choosing randomly, removing duplicates
            agent.local_conn = [1, 2, 3]
            self.agents_dict[str(i)] = agent

        # Exchange info between agents in the initial position
        self.exchange_information(0)

        count = 0
        assert self.th >= 0, \
            'threshold for end of experiment cannot be a negative value.'
        if self.th == 0:
            while self.perc_seen_ev < self.threshold:
                start_time = time.time()
                print("\nIteration " + str(count))
                for key in self.agents_dict.keys():
                    self.update_position(self.agents_dict[key], count)
                self.exchange_information(count)
                for key in self.agents_dict.keys():
                    self.send_info(self.agents_dict[key], count)
                print(f"percentage of events seen: {self.perc_seen_ev:0.2f}%")
                count += 1
                self.loop_duration.append(time.time() - start_time)
                self.mean_loop_duration.append(statistics.mean(self.loop_duration))
        else:
            while count < self.th:
                start_time = time.time()
                print("\nIteration " + str(count))
                for key in self.agents_dict.keys():
                    self.update_position(self.agents_dict[key], count)
                self.exchange_information(count)
                for key in self.agents_dict.keys():
                    self.send_info(self.agents_dict[key], count)
                print(f"percentage of events seen: {self.perc_seen_ev:0.2f}%")
                count += 1
                self.loop_duration.append(time.time() - start_time)
                self.mean_loop_duration.append(statistics.mean(self.loop_duration))
        return count

    def run(self):
        if self.store_latency:
            self.th = 0

        self.G = ox.load_graphml('graph/graph.graphml')
        self.onto.load()
        np.random.seed(self.seed)

        # collecting events in the environment
        for node in self.G.nodes(data=True):
            if node[1]['situation'] != 'None':
                self.events.append({
                    'situation': node[1]['situation'],
                    'object': node[1]['object'],
                    'where': node[0],
                    'mistaken': {'times': 0, 'difference': []},
                    'correct': 0,
                    'first_time': 0
                })

        inf = {'events': self.events, 'n_agents': self.n_agents,
               'n_gateways': math.floor(self.gateway_ratio * self.n_agents)}

        requests.put(self.BASE + "/IE/events", json.dumps(inf))

        ''' Running the simulation '''
        self.tic = time.perf_counter()
        self.num_loops = self.simulate()
        self.toc = time.perf_counter()

        pprint(self.events)

        print("Total time to get all events on the db: ", self.t_all)
        print(f"Experiment finished in {self.toc - self.tic:0.4f} seconds")

        if self.store_latency:
            try:
                if not os.path.exists(self.path + '/exp{0}/csv'.format(self.num_exp)):
                    os.makedirs(self.path + '/exp{0}/csv'.format(self.num_exp))
                if not os.path.exists(self.path + '/exp{0}/sent_to_db_loop'.format(self.num_exp)):
                    os.makedirs(self.path + '/exp{0}/sent_to_db_loop'.format(self.num_exp))
                if not os.path.exists(self.path + '/exp{0}/dir_obs_lats'.format(self.num_exp)):
                    os.makedirs(self.path + '/exp{0}/dir_obs_lats'.format(self.num_exp))
            except OSError:
                print('Error: Creating directory of data lats')

            if self.param == 'gateways':
                with open(self.path + '/exp{0}/sent_to_db_loop/{1}%_gateways.csv'.format(self.num_exp, str(round(self.gateway_ratio * 100, 1))),
                          'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['sent_to_db_loop'])
                    writer.writeheader()
                    for el in self.sent_at_loop:
                        writer.writerow({'sent_to_db_loop': el})
                with open(self.path + '/exp{0}/dir_obs_lats/{1}%_gateways.csv'.format(self.num_exp, str(round(self.gateway_ratio * 100, 1))),
                          'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['dir_obs_lats'])
                    writer.writeheader()
                    for el in self.dir_obs_latency:
                        writer.writerow({'dir_obs_lats': el})
            elif self.param == 'radius':
                with open(self.path + '/exp{0}/sent_to_db_loop/{1}Km_radius.csv'.format(self.num_exp, self.radius), 'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['sent_to_db_loop'])
                    writer.writeheader()
                    for el in self.sent_at_loop:
                        writer.writerow({'sent_to_db_loop': el})
                with open(self.path + '/exp{0}/dir_obs_lats/{1}Km_radius.csv'.format(self.num_exp, self.radius), 'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['dir_obs_lats'])
                    writer.writeheader()
                    for el in self.dir_obs_latency:
                        writer.writerow({'dir_obs_lats': el})
            else:
                with open(self.path + '/exp{0}/sent_to_db_loop/{1}_dev_std.csv'.format(self.num_exp, self.radius), 'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['sent_to_db_loop'])
                    writer.writeheader()
                    for el in self.sent_at_loop:
                        writer.writerow({'sent_to_db_loop': el})
                with open(self.path + '/exp{0}/dir_obs_lats/{1}_dev_std.csv'.format(self.num_exp, self.radius), 'w') as f:
                    writer = csv.DictWriter(f, fieldnames=['dir_obs_lats'])
                    writer.writeheader()
                    for el in self.dir_obs_latency:
                        writer.writerow({'dir_obs_lats': el})

            csv_files = sorted(glob('./*.csv'))
            for csv_f in csv_files:
                shutil.move(csv_f, './exp{0}/csv/'.format(self.num_exp))

        response = requests.delete(self.BASE + "IE/1")
        res = response.json()
        pprint(res)
