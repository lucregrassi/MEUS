import osmnx as ox
from person import Person
import random


def destination(graph, current_node):
    adj_nodes = list(n for n in graph[current_node])
    print("Adjacent nodes: " + str(adj_nodes))
    distance = 0
    destination_node = 0
    # If there are adjacent nodes
    if adj_nodes:
        destination_node = adj_nodes[0]
        edges_of_interest = G[current_node][destination_node]
        for edge in edges_of_interest.values():
            # May not have a length. Return None if this is the case.
            # Could save these to a new list, or do something else with them. Up to you.
            distance = edge.get('length')

    print("Destination node: " + str(destination_node))
    print("Distance: " + str(distance))
    return destination_node, distance


n_pers = 10

G = ox.load_graphml('images/graph.graphml')
G_copy = G

nodes = []
for node in G.nodes.data():
    nodes.append(node[0])

people = []
i = 1

# Position the persons in random nodes
for i in range(n_pers):
    curr_node = random.choice(nodes)
    print("Current node: " + str(curr_node))
    for elem in G.nodes.data():
        if elem[0] == curr_node:
            elem[1]['pers'] = int(elem[1]['pers']) + 1
    print(G[curr_node])
    dest_node, dist = destination(G, curr_node)
    person = Person(i, curr_node, dest_node, dist)
    person.visited_nodes.append(curr_node)
    print(person)
    print("\n")
    people.append(person)
    i += 1

fig, ax = ox.plot_graph(G, node_color='w', show=False)

removed_nodes = []
for node in G.nodes(data=True):
    if node[0] % 2 == 0:
        removed_nodes.append(node[0])

for node in removed_nodes:
    G.remove_node(node)

ox.plot_graph(G,  ax=ax, figsize=(8, 8), node_color='g', show=False)

removed_2 = []
for node in G.nodes(data=True):
    if node[0] % 5 == 0:
        removed_2.append(node[0])

for node in removed_2:
    G_copy.remove_node(node)

ox.plot_graph(G_copy, ax=ax, figsize=(8, 8), node_color='r', save=True, filepath="images/result.jpg")











