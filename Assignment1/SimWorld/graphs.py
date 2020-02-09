import networkx as nx
import matplotlib.pyplot as plt

# Not in usage
def drawGraph(layers=3, diamond=False):
    G = nx.Graph()

    if diamond:
        row = 2 * layers - 1
    else:
        row = layers

    n = 1
    for i in range(row):
        if diamond:
            if i < layers:
                n = draw_upper_triangle(G, n, layers, row, i)
            else:
                n = draw_lower_triangle(G, n, layers, row, i)

        else:
            n = draw_upper_triangle(G, n, layers, row, i)

    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx(G, pos)
    plt.show()


def draw_upper_triangle(G, n, layers, row, i):
    k = 0

    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        G.add_node(n, pos=(k, row - i))
        n += 1
        k += 2
    return n


def draw_lower_triangle(G, n, layers, row, i):
    k = 0
    for j in range(i - layers + 1, 0, -1):
        k += 1
    for j in range(row - i):
        G.add_node(n, pos=(k, row - i))
        n += 1
        k += 2
    return n

