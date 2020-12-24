import osmnx as ox
import random
from read_ontology import random_event

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
ox.config(all_oneway=True, useful_tags_node=utn, useful_tags_way=utw)
# Fetch OSM street network from the location
G = ox.graph_from_place(place, network_type='all')

G = ox.project_graph(G)
# G_simple = ox.simplify_graph(G, strict=True, remove_rings=True)

# Initialize content of nodes
for node in G.nodes(data=True):
    node[1]['pers'] = int(0)
    node[1]['situation'] = random_event()[0]
    node[1]['object'] = random_event()[1]
    node[1]['connection'] = '0'

# Plot the streets
# ox.plot_graph(G, filepath='images/graph.svg', save=True)
# ox.plot_graph(G, filepath='images/graph.png', save=True)

ox.save_graphml(G, filepath='graph/graph_temp.graphml')

