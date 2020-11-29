import osmnx as ox
from person import Person
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import glob
import os

n_pers = 200
steps = 100
loop_distance = 20

G = ox.load_graphml('graph/graph.graphml')


def color():
    node_color = []
    for node in G.nodes(data=True):
        if node[1]['pers'] == 1:
            node_color.append('r')
        elif node[1]['pers'] == 2:
            node_color.append('g')
        elif node[1]['pers'] == 3:
            node_color.append('b')
        else:
            node_color.append('w')
    return node_color


def compute_destination(current_node):
    source_nodes = []
    target_nodes = []
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
    # If there are adjacent nodes
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


def update_position(p):
    # print("\nUpdating position of person " + str(p.n))
    if not p.moving:
        previous_node = p.curr_node
        p.curr_node = p.dest_node
        destination_node, distance = compute_destination(p.dest_node)
        p.dest_node = destination_node
        p.distance = distance
        p.moving = True

        for n in G.nodes.data():
            if n[0] == previous_node:
                n[1]['pers'] = int(n[1]['pers']) - 1
            elif n[0] == p.curr_node:
                n[1]['pers'] = int(n[1]['pers']) + 1

        p.visited_nodes.append(p.curr_node)
    else:
        # If the person is moving, check if it has reached the destination
        if p.distance > 0:
            # If it has not reached the destination, move
            p.distance = p.distance - loop_distance
        else:
            p.moving = False
    # print(p)


def create_gif():
    frames = []
    for j in range(0, steps):
        img = "images/img" + str(j) + ".png"
        print(img)
        new_frame = Image.open(img)
        frames.append(new_frame)

    frames[0].save("simulation.gif", format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=500, Loop=0)


people = []
i = 1

# Initialize people position in random nodes
for i in range(n_pers):
    curr_node = random.choice(list(n[0] for n in G.nodes.data()))
    for elem in G.nodes.data():
        if elem[0] == curr_node:
            elem[1]['pers'] = int(elem[1]['pers']) + 1
            # print(elem)
    dest_node, dist = compute_destination(curr_node)
    person = Person(i, curr_node, dest_node, dist)
    person.visited_nodes.append(curr_node)
    people.append(person)
    i += 1

nc = color()
ox.plot_graph(G, node_color=nc, show=False, save=True, filepath="images/img0.png")
plt.close()

for i in range(1, steps):
    print("\nIteration " + str(i))
    for pers in people:
        update_position(pers)

    # print("Printing")
    img_path = "images/img" + str(i) + ".png"
    nc = color()
    ox.plot_graph(G, node_color=nc, show=False, save=True, filepath=img_path)
    plt.close()


create_gif()





