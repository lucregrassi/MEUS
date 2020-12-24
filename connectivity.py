import math
import random
import osmnx as ox


G = ox.load_graphml('graph/graph_temp.graphml')


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


def setup_connection(graph, connection, hubs, radius):
    nodes = random.choices(list(graph.nodes), k=hubs)
    for node in graph.nodes(data=True):
        if node[0] in nodes:
            node[1]['connection'] = str(node[1]['connection']) + str(connection)
            if '0' in node[1]['connection']:
                node[1]['connection'] = node[1]['connection'][1:]

            print(node)
            kmInLongitudeDegree = 111.320 * math.cos(node[1]['lat'] / 180.0 * math.pi)
            deltaLat = radius / 111.1
            deltaLong = radius / kmInLongitudeDegree

            minLat = node[1]['lat'] - deltaLat
            maxLat = node[1]['lat'] + deltaLat
            minLong = node[1]['lon'] - deltaLong
            maxLong = node[1]['lon'] + deltaLong

            for n in graph.nodes(data=True):
                if minLong < n[1]['lon'] < maxLong and minLat < n[1]['lat'] < maxLat:
                    if str(connection) not in n[1]['connection']:
                        n[1]['connection'] = str(n[1]['connection']) + str(connection)
                        if '0' in list(n[1]['connection']):
                            n[1]['connection'] = n[1]['connection'][1:]
    return graph


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

ox.save_graphml(G, filepath='graph/graph.graphml')

nc = color(G)
ox.plot_graph(G, node_color=nc, node_size=20, show=True, save=True, filepath="images/conn.png")