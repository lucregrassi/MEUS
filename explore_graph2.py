import copy
import math
import random
import logging
import osmnx as ox
from PIL import Image
from Agent import Agent
import matplotlib.pyplot as plt
from read_ontology import get_cls_at_dist
from InformationElement import NewInformationElement, NewDirectObservation

import matplotlib.pyplot as plt
from shapely.geometry import LineString
from utils import preProcessing, IEtoDict
import requests
import json
import pprint


BASE = "http://127.0.0.1:5000/"

plt.style.use('fivethirtyeight')
logging.basicConfig(level=logging.DEBUG, filename='explore_graph.log', filemode='w')

# Initialize number of agents exploring the graph
n_agents = 200
# Number of iterations
steps = 20
# Distance traveled (in meters) by each person in one loop cycle
loop_distance = 20

# Instances of agents moving in the graph
agents_dict = {}
# Dictionary where the keys are the nodes and the values are lists containing the IDs of agents in those nodes
node_state_dict = {}

# Load the graph from the graphml file previously saved
G = ox.load_graphml('graph/graph.graphml')


# This function returns an array containing the colors of each node, based on the number of people
def color():
    node_color = []
    for node in G.nodes(data=True):
        if node[1]['n_agents'] == 1:
            node_color.append('#AAA')
        elif node[1]['n_agents'] == 2:
            node_color.append('#7F7F7F')
        elif node[1]['n_agents'] == 3:
            node_color.append('#333')
        else:
            node_color.append('w')
    return node_color


def compute_intermediate_dist(target_edge):
    dist = []
    path = {}
    for i in range(len(target_edge['geometry'].coords)-1):
        # distance between each and every subnode
        dist = math.sqrt(   (target_edge['geometry'].coords[i][0] - target_edge['geometry'].coords[i+1][0])**2 + \
                            (target_edge['geometry'].coords[i][1] - target_edge['geometry'].coords[i+1][1])**2)
        path[str(i+1) + '-' + str(i+2)] = {'edgeID': target_edge['osmid'], 'dist': dist, \
                                                'UTM_coordinates': [target_edge['geometry'].coords[i], target_edge['geometry'].coords[i+1]]}
        
    return path


def geolocalise_me(agent):
    logging.info("| geolocalise_me()")
    rel_dist = 0

    # if the agent has yet to reach the destination node
    if agent.road < agent.distance:
        for key in agent.path:
            # if I am between the first couple of subnodes in the path
            rel_dist += agent.path[key]['dist']
            if (agent.road <= rel_dist):
                # logging.info("Agent: " + str(agent.n) + ". counter: " + str(counter) + "\n \
                #     my destination is at " + str(agent.distance) +"[m], I have traveled " + str(agent.road) + " [m]. I am between positions: " + \
                #     str(agent.path[key]['UTM_coordinates']) + ".")

                x2 = agent.path[key]['UTM_coordinates'][1][0]
                x1 = agent.path[key]['UTM_coordinates'][0][0]

                y2 = agent.path[key]['UTM_coordinates'][1][1]
                y1 = agent.path[key]['UTM_coordinates'][0][1]


                l    = agent.road - (rel_dist - agent.path[key]['dist'])
                L = agent.path[key]['dist']

                x = x1 + (x2-x1)*l/L
                y = y1 + (y2-y1)*l/L

                estimated_UTM = (x, y)

                return estimated_UTM

    elif agent.road==agent.distance:
        logging.info("I am on the destination node")
    else:
        logging.info("traveled road is > than agent.distance. \ntraveled_road: " +str(agent.road) + "\nagent.distance: " +str(agent.distance))

    logging.info("| returning from geolocalise_me()")


# This function computes the destination node, based on the current node - the destination is randomly chosen among
# adjacent nodes. It returns the destination node and the distance (in meters) from it.
def compute_destination(current_node):
    source_nodes = []
    target_nodes = []
    # Look for all the sources and the targets of the current node
    for e in G.edges():
        source, target = e
        if source == current_node:
            target_nodes.append(target)
        if target == current_node:
            source_nodes.append(source)
    # print("Source nodes of " + str(current_node) + ": " + str(source_nodes))
    # print("Target nodes of " + str(current_node) + ": " + str(target_nodes))
    adj_nodes = source_nodes + target_nodes
    # print("All adjacent nodes: " + str(adj_nodes))
    distance = 0
    destination_node = 0
    # If there are adjacent nodes (at least a source or a target), pick one randomly as the destination
    if adj_nodes:
        destination_node = random.choice(adj_nodes)
        # print("Destination node: " + str(destination_node))
        if destination_node in target_nodes:
            edges_of_interest = G[current_node][destination_node]
        else:
            edges_of_interest = G[destination_node][current_node]
        for edge in edges_of_interest.values():
            distance = edge.get('length')
            ls = compute_intermediate_dist(edge)
            if distance < 0:
                logging.error("distance is negative!!!")
    return destination_node, distance, ls


# Function called after the initialization (loop 0) and after the update of the positions in each loop
def exchange_information(loop):
    delete = []
    # old_listeners_ies = []
    for k in node_state_dict.keys():
        # If there is more than one agent in a node, they should exchange their info
        if len(node_state_dict[k]) > 1:
            delete.append(k)
            for agent_id in node_state_dict[k]:
                listener = agents_dict[str(agent_id)] 
                for ag_id in node_state_dict[k]:
                    # If the teller has a different id (is not the listener), and if they both have
                    candidate = agents_dict[str(ag_id)]
                    if candidate.n != listener.n:
                        perform_exchange = False
                        # Look for common local connections
                        if any(j in candidate.local_conn for j in listener.local_conn):
                            print("\nCommon local connection found for agents ", candidate.n, "and", listener.n)
                            perform_exchange = True
                        else:
                            print("\nNo common local connections found bewteen", candidate.n, "and", listener.n)
                            print("Looking for global connections...")
                            # Check global connections if no common local connection is found
                            common_global = [value for value in candidate.global_conn if value in listener.global_conn]
                            print("Listener", listener.n, "->", listener.global_conn)
                            print("Teller", candidate.n, "->", candidate.global_conn)
                            print("Common global connections: ", common_global)
                            # If there is a common global connection, check if the connection is available in that node
                            if common_global:
                                node_conn = G.nodes[int(k)]['connection']
                                print("Node", k, "connections: ", list(node_conn))
                                for conn in common_global:
                                    if str(conn) in node_conn:
                                        print("Common global connection", conn, "found in node!", )
                                        perform_exchange = True
                                        break
                                if not perform_exchange:
                                    print("Common global connection not available in the node :(")
                            else:
                                print("No common global connections!")
                        # If there is at least a common local connection or a common global connection available
                        if perform_exchange:
                            teller = candidate
                            listener.met_agents.append(teller.n)
                            listener.met_in_node.append(int(k))
                            listener.met_in_loop.append(loop)
                            print("teller("+str(teller.n)+"):" )
                            for ie in teller.ies:
                                # print(ie)
                                print(ie[0], ",", ie[1:])
                            print("listener("+str(listener.n)+"):")
                            for ie in listener.ies:
                                # print(ie)
                                print(ie[0], ",", ie[1:])
                            # Loop through all Information Elements of the teller
                            for IE_teller in teller.ies:
                                same_root = False
                                already_told = False
                                # same_root_IE_listener = []
                                # Loop through all Information Elements of the listener
                                # for IE_listener in listener.ies:
                                #     # If the IEs have the same root (can happen only once)
                                #     if IE_teller[0] == IE_listener[0]:
                                #         same_root = True
                                #         # same_root_IE_listener = copy.deepcopy(IE_listener)
                                #         # For each quadrupla in the IE
                                #         for quadrupla in IE_teller[1:]:
                                #             # If the listener is not a teller in a tuple of the IE,
                                #             # or the teller has not previously told the information to the listener
                                #             if quadrupla[0] == listener.n or \
                                #                     (quadrupla[0] == teller.n and quadrupla[1] == listener.n):
                                #                 already_told = True
                                for i in range(len(listener.ies)):
                                    # If the IEs have the same root (can happen only once)
                                    if IE_teller[0] == listener.ies[i][0]:
                                        same_root = True
                                        index = i
                                        # same_root_IE_listener = copy.deepcopy(IE_listener)
                                        # For each quadrupla in the IE
                                        for quadrupla in IE_teller[1:]:
                                            # If the listener is not a teller in a tuple of the IE,
                                            # or the teller has not previously told the information to the listener
                                            if quadrupla[0] == listener.n or \
                                                    (quadrupla[0] == teller.n and quadrupla[1] == listener.n):
                                                already_told = True
                                                break

                                if not already_told:
                                    if same_root:
                                        # same_root_IE_listener.append((teller.n, listener.n, int(k), loop))
                                        if len(IE_teller[1:]) > 0:
                                            target_extend = []
                                            target_extend.append((teller.n, listener.n, int(k), loop))
                                            for elem in IE_teller[1:]:
                                                target_extend.append(elem)
                                            # communicating the information to the listener
                                            listener.ies[index].extend(target_extend)
                                        else:
                                            listener.ies[index].append((teller.n, listener.n, int(k), loop))
                                        print("###################################################")
                                        print("I have added:")
                                        print(listener.ies[index][0], ", ", listener.ies[index][1:])
                                        input("check")
                                    else:
                                        # Append the new IE to the listener (making a deepcopy of the IE of the teller)
                                        listener.ies.append(copy.deepcopy(IE_teller))
                                        listener.ies[-1].append((teller.n, listener.n, int(k), loop))
    # Avoid that they can meet again once they exchange their info and they are still in the same node
    for k in delete:
        del node_state_dict[k]


# Update a specific person's attributes
def update_position(a, loop):
    # print("\nUpdating position of person " + str(p.n))
    # Update only if the person is not moving
    logging.info("| update_position()")
    if not a.moving:
        # Arrived to destination node
        previous_node                       = a.curr_node
        a.curr_node                         = a.dest_node
        destination_node, distance, path    = compute_destination(a.dest_node)
        a.dest_node                         = destination_node
        a.distance                          = distance
        a.path                              = path
        a.moving                            = True
        a.road                              = 0

        node_situation = []
        node_object = []
        # Update the counters in the nodes and acquire the situation and the object in the new current node
        for n in G.nodes.data():
            if n[0] == previous_node:
                n[1]['n_agents'] = int(n[1]['n_agents']) - 1
                # If it has still not been removed from that node, delete it so that no exchange is possible
                if str(n[0]) in node_state_dict:
                    if a.n in node_state_dict[str(n[0])]:
                        node_state_dict[str(n[0])].remove(a.n)

            elif n[0] == a.curr_node:
                n[1]['n_agents'] = int(n[1]['n_agents']) + 1
                # if this node is not yet in the dictionary, create the key-value pair
                if not node_state_dict.get(str(n[0])):
                    node_state_dict[str(n[0])] = [a.n]
                # if the node is already in the dictionary, append to the value the agent's id
                else:
                    node_state_dict[str(n[0])].append(a.n)

                node_situation = n[1]['situation']
                node_object = n[1]['object']

        # Add the new current node to the list of visited nodes of the person
        a.visited_nodes.append(a.curr_node)
        # The actual situation and object seen by the person depend on its trustworthiness
        seen_sit = get_cls_at_dist(node_situation, a.error)
        seen_obj = get_cls_at_dist(node_object, a.error)
        seen_ev = seen_sit, seen_obj
        a.seen_events.append(seen_ev)
        # Add what the person thinks to have seen to its list of information elements
        # root = NewDirectObservation(a.n, a.curr_node, loop, seen_ev, a.error)
        a.ies.append([NewInformationElement(a.n, a.curr_node, loop, NewDirectObservation(seen_ev, a.error))])
    else:
        # If the person is moving, check if it has reached the destination
        if a.distance > 0:
            # If it has not reached the destination, move of the defined distance
            a.distance = a.distance - loop_distance
            a.road += loop_distance 
            geolocalise_me(a)

        else:
            # If the distance is 0 or negative it means that the destination has been reached
            a.moving = False
            # here maybe to recompute the destination for a second time
    logging.info("| returning from update_position()")


def send_info(agent):

    conn = G.nodes.get(agent.curr_node)['connection']
    conn = conn.split(",")
    conn_new = [int(i) for i in conn]

    # input("check 1")

    if len(agent.global_conn) > 0 and any(conn_new) and len(agent.ies) > 0 and agent.num_info_sent < len(agent.ies):
        # input("check 2")
    # if agent.n > 100 and len(agent.ies) and agent.num_info_sent < len(agent.ies):
        knowledge = []
        # if agent.num_info_sent >= len(agent.ies):
        #     print("agent.num_info_sent: ", agent.num_info_sent)
        #     print("len(agent.ies): ", len(agent.ies))
        #     input("send_info()")
        for i in range(agent.num_info_sent, len(agent.ies)):
            copia_ie = copy.deepcopy(agent.ies[i])
            copia_ie = IEtoDict(copia_ie)
            knowledge.append(copia_ie)

        print("knowledge: " +str(knowledge))
        response = requests.put(BASE + "IE/1", json.dumps(knowledge))
        print(response.json())
        agent.num_info_sent += len(agent.ies)
        # input("check 3")
        # agent.ies.clear()
    else:
        # input("check 4")
        logging.info("| It has not been possible to send information to the database!")




# This function generates a GIF starting from the images
def create_gif():
    frames = []
    for j in range(0, steps):
        img = "images/img" + str(j) + ".png"
        new_frame = Image.open(img)
        frames.append(new_frame)

    frames[0].save("simulation.gif", format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=500, Loop=0)


i = 1
# Initialize people's positions in random nodes
for i in range(n_agents):
    curr_node = random.choice(list(n[0] for n in G.nodes.data()))
    situation = {}
    obj = []
    # Update the counter of the number of people in that node and get the situation and the object
    for elem in G.nodes(data=True):
        if elem[0] == curr_node:
            # Increment the number of people in that node
            elem[1]['n_agents'] = int(elem[1]['n_agents']) + 1
            # Add person id to the node
            if not node_state_dict.get(str(curr_node)):
                node_state_dict[str(curr_node)] = [i]
            else:
                node_state_dict[str(curr_node)].append(i)

            situation = elem[1]['situation']
            obj = elem[1]['object']
            # print("situation: " + str(situation))
            # print("obj: " + str(obj))
            # print("elem[1]: " + str(elem[1]))
            # input("hit enter")

    dest_node, dist, path = compute_destination(curr_node)
    # Instantiate the Person class passing the arguments
    agent = Agent(i, curr_node, dest_node, dist, path, random.randint(0, 2))
    agent.visited_nodes.append(curr_node)

    # Add the event that the person thinks to have seen to the list
    seen_situation = get_cls_at_dist(situation, agent.error)
    seen_object = get_cls_at_dist(obj, agent.error)
    seen_event = (seen_situation, seen_object)

    # print("seen situation: " +str(seen_situation))
    # print("seen object: " +str(seen_object))
    # print("seen event: " +str(seen_event))
    # input("hit enter")

    agent.seen_events.append(seen_event)
    # ie_root = InformationElement(i, [i], curr_node, 0, DirectObservation(seen_event, agent.error))
    # agent.ies.append(InformationElement(i, [i], curr_node, 0, DirectObservation(seen_event, agent.error), ie_root))
    agent.ies.append([NewInformationElement(i, curr_node, 0, NewDirectObservation(seen_event, agent.error))])
    # Initialize the connections owned by the person
    agent.global_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
    # Initialize array of local connections, choosing randomly, removing duplicates
    agent.local_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
    agents_dict[str(i)] = agent
    i += 1

logging.info("| DESTINATIONS COMPUTED")

# Array of colors of the nodes based on the number of people contained
nc = color()
# Save the initial graph (with people in their starting position)
ox.plot_graph(G, node_color=nc, node_size=20, show=False, save=True, filepath="images/img0.png")
plt.close()

# Exchange info between agents in the initial position
exchange_information(0)

# Print the state of all the agents along with their IEs
for key in agents_dict.keys():
    print(agents_dict[key])
    for ie in agents_dict[key].ies:
        # print(ie)
        print(ie[0], ",", ie[1:])


# Loop through the predefined # of steps and update the agent's positions
for i in range(1, steps):
    print("\nIteration " + str(i))
    for key in agents_dict.keys():
        # Update the position of the agent
        update_position(agents_dict[key], i)
    logging.info("bigcounter: " +str(i))

    exchange_information(i)
    #  Print the updated state of the agents along with their IEs
    for key in agents_dict.keys():
        print(agents_dict[key])
        # print("type(agents_dict[key].ies): " + str(type(agents_dict[key].ies)))
        for ie in agents_dict[key].ies:
            # print(ie)
            print(ie[0], ",", ie[1:])
        # send_info(agents_dict[key])
    logging.info("#############################SENT INFO STEP"+str(i)+" #########################")

    # Define the path of the image in which the updated graph will be saved
    img_path = "images/img" + str(i) + ".png"
    # Initialize color map on the basis of the people in each node
    nc = color()
    # Save the graph with the updated positions in the image
    ox.plot_graph(G, node_color=nc, node_size=20, show=False, save=True, filepath=img_path)
    plt.close()

# input("check 2 explore_graph.py")
# response = requests.get(BASE + "IE/1" )
# pprint.pprint(response.json())


# input("check 3 explore_graph.py")
# response = requests.delete(BASE + "IE/1" )
# pprint.pprint(response.json()) 


# Generate the GIF from the saved sequence of images
create_gif()
