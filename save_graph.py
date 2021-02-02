import osmnx as ox
from read_ontology import random_event

# OSMnx documentation
# https://osmnx.readthedocs.io/en/stable/osmnx.html

# Specify the name that is used to search for the data
place = 'Frabosa Soprana, Cuneo, Piemonte'

utn = ox.settings.useful_tags_node
oxna = ox.settings.osm_xml_node_attrs
oxnt = ox.settings.osm_xml_node_tags
utw = ox.settings.useful_tags_way
oxwa = ox.settings.osm_xml_way_attrs
oxwt = ox.settings.osm_xml_way_tags
utn = list(set(utn + oxna + oxnt))
utw = list(set(utw + oxwa + oxwt))

# Set configurations used when importing the graph
ox.config(all_oneway=True, useful_tags_node=utn, useful_tags_way=utw)
# Fetch OSM street network from the location
G = ox.graph_from_place(place, network_type='all')

# Project the graph to the UTM CRS for the UTM zone in which the graph’s centroid lies
G = ox.project_graph(G)

# Simplify a graph’s topology by removing interstitial nodes
# G_simple = ox.simplify_graph(G, strict=True, remove_rings=True)

# Initialize content of nodes
for node in G.nodes(data=True):
    # Number of people in that node
    node[1]['n_agents'] = '0'
    node[1]['situation'] = random_event()[0]
    node[1]['object'] = random_event()[1]
    # Type of connection available in the node
    node[1]['connection'] = '0'
    # print(node)


# Save the graph in a graphml file
# Note: the file is named "temp" because the connections are still not initialized.
ox.save_graphml(G, filepath='graph/graph_temp.graphml')

