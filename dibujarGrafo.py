#!/usr/bin/python3
# -*- coding: utf-8 -*-

import networkx as nx
import random
import matplotlib.pyplot as plt

# grafo de n nodos donde la probabilidad de que un eje exista es de p
def dibujarChord(nodes):
    G = nx.DiGraph()
    for i in range(len(nodes)):
        G.add_node(nodes[i])
    
    for i in range(len(nodes)):
        if i < len(nodes) -1:
            G.add_edge(nodes[i],nodes[i+1])
        else:
            G.add_edge(nodes[i],nodes[0])
        
    edge_labels = nx.get_edge_attributes(G, 'weight')
    label = nx.nodes(G)

    nx.draw_shell(G,with_labels=True, edge_labels=edge_labels)

    plt.show()
'''
nodes = [1,2,3,4,5]
dibujarChord(nodes)
'''