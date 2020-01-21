import networkx as nx
import matplotlib.pyplot as plt

def drawGraph(layers = 3, diamond=False):

    G = nx.Graph()

    nodes = []

    col = (2 * layers - 1)

    if (diamond): row = 2 * layers - 1
    else: row = layers

    # Loop to dispaly board, can be used to initialize coordinates for peg-objects
    n = 1
    for i in range(row):
        k = 0
        if (diamond):
            if (i < layers):
                for j in range(layers-i-1):
                    k += 1
                for j in range(i+1):
                    print(f"n = {n}, ({k},{row - i})")
                    G.add_node(n, pos=(k, row - i))
                    n += 1
                    k += 2
            #lower part of diamond
            else:
                for j in range(i-layers+1, 0, -1):
                    k += 1
                for j in range(row-i):
                    print(f"n = {n}, ({k},{row - i})")
                    G.add_node(n, pos=(k, row - i))
                    n += 1
                    k += 2
        else:
            for j in range(layers-i-1):
                k += 1
            for j in range(i+1):
                G.add_node(n, pos=(k,row-i))
                n += 1
                k += 2

    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx(G, pos)
    plt.show()

drawGraph(layers=5,diamond=False)