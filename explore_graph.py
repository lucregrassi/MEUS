import osmnx as ox
from person import Person
import random
import matplotlib.pyplot as plt
from PIL import Image
from read_ontology import get_cls_at_dist

# Initialize number of people exploring the graph
n_pers = 200
# Number of iterations
steps = 10
# Distance traveled (in meters) by each person in one loop cycle
loop_distance = 20

# Load the graph from the graphml file previously saved
G = ox.load_graphml('graph/graph.graphml')


# This function returns an array containing the colors of each node, based on the number of people
def color():
    node_color = []
    for node in G.nodes(data=True):
        if node[1]['pers'] == 1:
            node_color.append('#AAA')
        elif node[1]['pers'] == 2:
            node_color.append('#7F7F7F')
        elif node[1]['pers'] == 3:
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


# Update a specific person's attributes
def update_position(p):
    # print("\nUpdating position of person " + str(p.n))
    # Update only if the person is not moving
    if not p.moving:
        previous_node = p.curr_node
        p.curr_node = p.dest_node
        destination_node, distance = compute_destination(p.dest_node)
        p.dest_node = destination_node
        p.distance = distance
        p.moving = True

        node_situation = []
        node_object = []
        # Update the counters in the nodes and acquire the situation and the object in the new current node
        for n in G.nodes.data():
            if n[0] == previous_node:
                n[1]['pers'] = int(n[1]['pers']) - 1
            elif n[0] == p.curr_node:
                n[1]['pers'] = int(n[1]['pers']) + 1
                node_situation = n[1]['situation']
                node_object = n[1]['object']

        # Add the new current node to the list of visited nodes of the person
        p.visited_nodes.append(p.curr_node)
        # The actual situation and object seen by the person depend on its trustworthiness
        seen_sit = get_cls_at_dist(node_situation, p.error)
        seen_obj = get_cls_at_dist(node_object, p.error)
        seen_ev = seen_sit, seen_obj
        # Add what the person thinks to have seen to its list of seen events
        p.seen_events.append(seen_ev)
    else:
        # If the person is moving, check if it has reached the destination
        if p.distance > 0:
            # If it has not reached the destination, move of the defined distance
            p.distance = p.distance - loop_distance
        else:
            # If the distance is 0 or negative it means that the destination has been reached
            p.moving = False
    print(p)


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


people = []
i = 1

# Initialize people's positions in random nodes
for i in range(n_pers):
    curr_node = random.choice(list(n[0] for n in G.nodes.data()))
    situation = {}
    obj = []
    # Update the counter of the number of people in that node and get the situation and the object
    for elem in G.nodes(data=True):
        if elem[0] == curr_node:
            elem[1]['pers'] = int(elem[1]['pers']) + 1
            situation = elem[1]['situation']
            obj = elem[1]['object']

    dest_node, dist = compute_destination(curr_node)
    # Instantiate the Person class passing the arguments
    person = Person(i, curr_node, dest_node, dist, random.randint(0, 2))
    person.visited_nodes.append(curr_node)

    # Add the event that the person thinks to have seen to the list
    seen_situation = get_cls_at_dist(situation, person.error)
    seen_object = get_cls_at_dist(obj, person.error)
    seen_event = seen_situation, seen_object
    person.seen_events.append(seen_event)

    # Initialize the connections owned by the person
    # person.global_conn.append(random.choices([1, 2, 3], k=random.randint(1, 3))
    # person.local_conn.append(random.choices([1, 2, 3], k=random.randint(1, 3))
    people.append(person)
    i += 1


# Array of colors of the nodes based on the number of people contained
nc = color()
# Save the initial graph (with people in their starting position)
ox.plot_graph(G, node_color=nc, node_size=20, show=False, save=True, filepath="images/img0.png")
plt.close()

# Loop through the predefined # of steps and update the people's positions
for i in range(1, steps):
    print("\nIteration " + str(i))
    for pers in people:
        update_position(pers)

    # Define the path of the image in which the updated graph will be saved
    img_path = "images/img" + str(i) + ".png"
    # Initialize color map on the basis of the people in each node
    nc = color()
    # Save the graph with the updated positions in the image
    ox.plot_graph(G, node_color=nc, node_size=20, show=False, save=True, filepath=img_path)
    plt.close()

# Generate the GIF from the saved sequence of images
create_gif()





