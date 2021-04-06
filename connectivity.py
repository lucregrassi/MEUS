import math
import random
import osmnx as ox

# Load the "temporary" graph saved
G = ox.load_graphml('graph/graph_temp.graphml')


# This function returns a list containing the colors of the nodes on the basis of the available connections
# Note: if a node has multiple types of connections, only one color is shown.
def color(graph):
    node_color = []
    for node in graph.nodes(data=True):
        if '1' in node[1]['connection']:
            node_color.append('r')
        elif '2' in node[1]['connection']:
            node_color.append('g')
        elif '3' in node[1]['connection']:
            node_color.append('b')
        else:
            node_color.append('w')
    return node_color


# This function randomly picks as many nodes as the number of hubs specified as parameter, and
def setup_connection(graph, connection, hubs, radius):
    nodes = random.choices(list(graph.nodes), k=hubs)
    for node in graph.nodes(data=True):
        # If the node is an hub
        if node[0] in nodes:
            print(node)
            # check that the hub does not already have that connection
            if str(connection) not in node[1]['connection']:
                # Add the connection passed as parameter to the connections of that node
                node[1]['connection'] = str(node[1]['connection']) + str(connection)
                # If the node does not have any connections yet, remove the placeholder '0', and add the connection
                if '0' in node[1]['connection']:
                    node[1]['connection'] = node[1]['connection'][1:]

            # On the basis of the radius, compute the area of the map covered by that connection
            kmInLongitudeDegree = 111.320 * math.cos(node[1]['lat'] / 180.0 * math.pi)
            deltaLat = radius / 111.1
            deltaLong = radius / kmInLongitudeDegree

            minLat = node[1]['lat'] - deltaLat
            maxLat = node[1]['lat'] + deltaLat
            minLong = node[1]['lon'] - deltaLong
            maxLong = node[1]['lon'] + deltaLong

            # Add that connection (if not already present) to all the nodes in the area inside the interval
            for n in graph.nodes(data=True):
                if minLong < n[1]['lon'] < maxLong and minLat < n[1]['lat'] < maxLat:
                    if str(connection) not in n[1]['connection']:
                        n[1]['connection'] = str(n[1]['connection']) + ',' + str(connection) + ','
                        if '0' in list(n[1]['connection']):
                            n[1]['connection'] = n[1]['connection'][2:]
                # Remove final comma if present
                if n[1]['connection'][-1] == ',':
                    n[1]['connection'] = n[1]['connection'][:-1]
    return graph


# Define the number of hubs (sources) and the radius for each type of connection

# Setup 4g connections
hubs_4g = 1
radius_4g = 1
G = setup_connection(G, 1, hubs_4g, radius_4g)

# Setup 5g connections
hubs_5g = 1
radius_5g = 1
G = setup_connection(G, 2, hubs_5g, radius_5g)

# Setup Wi-Fi connections
hubs_wifi = 1
radius_wifi = 1
G = setup_connection(G, 3, hubs_wifi, radius_wifi)

# Save the graph with the connections initialized
ox.save_graphml(G, filepath='graph/graph.graphml')

# Plot and save the image showing the areas covered by the connections
# Note: red=4g, green=5g, blue=Wi-Fi
nc = color(G)
ox.plot_graph(G, node_color=nc, node_size=20, show=True, save=True, filepath="images/conn.png")