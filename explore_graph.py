import osmnx as ox
import copy
from Agent import Agent
import random
import matplotlib.pyplot as plt
from PIL import Image
from read_ontology import get_cls_at_dist
from InformationElement import InformationElement, DirectObservation

# Initialize number of agents exploring the graph
n_agents = 200
# Number of iterations
steps = 10
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

    # print("Distance: " + str(distance))
    return destination_node, distance


# Function called after the initialization (loop 0) and after the update of the positions in each loop
def exchange_information(loop):
    delete = []
    for k in node_state_dict.keys():
        # If there is more than one agent in a node, they should exchange their info
        if len(node_state_dict[k]) > 1:
            delete.append(k)
            # print("\nINFORMATION EXCHANGE")
            # print(k, node_state_dict[k])
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
                        # If there is at least a common local connections or a common global connection available
                        if perform_exchange:
                            teller = candidate
                            listener.met_agents.append(teller.n)
                            listener.met_in_node.append(int(k))
                            listener.met_in_loop.append(loop)
                            # Loop through all Information Elements of the teller
                            for in_el in teller.ies:
                                already_told = False
                                # Loop through all Information Elements of the listener
                                for inf_el in listener.ies:
                                    # If the IEs have the same root
                                    if in_el.root == inf_el.root:
                                        # If the listener is not already in the history of the IE of the teller
                                        if listener.n in in_el.history:
                                            already_told = True
                                if not already_told:
                                    # Deepcopy the history of the teller to avoid references!!
                                    hist = copy.deepcopy(in_el.history)
                                    # Add the listener id to create the history of its new IE
                                    hist.append(listener.n)
                                    # Append the new IE to the listener
                                    listener.ies.append(InformationElement(teller.n, hist, int(k), loop, in_el, in_el.root))
    # Avoid that they can meet again once they exchange their info and they are still in the same node
    for k in delete:
        del node_state_dict[k]


# Update a specific person's attributes
def update_position(a, loop):
    # print("\nUpdating position of person " + str(p.n))
    # Update only if the person is not moving
    if not a.moving:
        # Arrived to destination node
        previous_node = a.curr_node
        a.curr_node = a.dest_node
        destination_node, distance = compute_destination(a.dest_node)
        a.dest_node = destination_node
        a.distance = distance
        a.moving = True

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
        root = InformationElement(a.n, [a.n], a.curr_node, loop, DirectObservation(seen_ev, a.error))
        a.ies.append(InformationElement(a.n, [a.n], a.curr_node, loop, DirectObservation(seen_ev, a.error), root))
    else:
        # If the person is moving, check if it has reached the destination
        if a.distance > 0:
            # If it has not reached the destination, move of the defined distance
            a.distance = a.distance - loop_distance
        else:
            # If the distance is 0 or negative it means that the destination has been reached
            a.moving = False


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

    dest_node, dist = compute_destination(curr_node)
    # Instantiate the Person class passing the arguments
    agent = Agent(i, curr_node, dest_node, dist, random.randint(0, 2))
    agent.visited_nodes.append(curr_node)

    # Add the event that the person thinks to have seen to the list
    seen_situation = get_cls_at_dist(situation, agent.error)
    seen_object = get_cls_at_dist(obj, agent.error)
    seen_event = (seen_situation, seen_object)

    agent.seen_events.append(seen_event)
    ie_root = InformationElement(i, curr_node, 0, DirectObservation(seen_event, agent.error))
    agent.ies.append(InformationElement(i, [i], curr_node, 0, DirectObservation(seen_event, agent.error), ie_root))
    # Initialize the connections owned by the person
    agent.global_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
    # Initialize array of local connections, choosing randomly, removing duplicates
    agent.local_conn = list(dict.fromkeys(random.choices([1, 2, 3], k=random.randint(1, 3))))
    agents_dict[str(i)] = agent
    i += 1

# print(agents_dict)
# print(node_state_dict)

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
        print(ie)

# Loop through the predefined # of steps and update the agent's positions
for i in range(1, steps):
    print("\nIteration " + str(i))
    for key in agents_dict.keys():
        # Update the position of the agent
        update_position(agents_dict[key], i)

    exchange_information(i)

    # # Print the updated state of the agents along with their IEs
    for key in agents_dict.keys():
        print(agents_dict[key])
        for ie in agents_dict[key].ies:
            print(ie)

    # Define the path of the image in which the updated graph will be saved
    img_path = "images/img" + str(i) + ".png"
    # Initialize color map on the basis of the people in each node
    nc = color()
    # Save the graph with the updated positions in the image
    ox.plot_graph(G, node_color=nc, node_size=20, show=False, save=True, filepath=img_path)
    plt.close()

# Generate the GIF from the saved sequence of images
create_gif()
