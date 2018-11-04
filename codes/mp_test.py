import mapper_functions as mf
import networkx as nx
from models import Node
import random as rand

def createNodes(n):
    c = 97
    nodes = []
    for i in range(n):
        nodes.append(Node(chr(c+i)))
    
    return nodes

def addProperty(prop, nodes):
    rand.seed(0)
    for i, node in enumerate(nodes):
        node.__dict__[prop] = rand.random()*100
    
    for node in nodes:
        node.id_0 = ord(node.name)%97

    return nodes

def buildGraph(nodes):
    g = nx.DiGraph()
    c = nodes[2]
    for i in range(3):
        if i < 2:
            g.add_edge(c,nodes[i])
        else:
            g.add_edge(c,nodes[i+1])
    
    g.add_edge(nodes[3],nodes[6])
    g.add_edge(nodes[4],nodes[5])
    g.add_edge(nodes[4],nodes[6])

    return g

def buildStudyGraph(nodes):
    g = nx.Graph()
    n = len(nodes)//2
    i = 0
    for _ in range(n):
        g.add_edge(nodes[i],nodes[i+1])   
        g.add_edge(nodes[rand.randint(0,n*2)],nodes[rand.randint(0,n*2)])      
        i += 2

    return g


if __name__ == "__main__":
    nodes = createNodes(10)
    prop = "readingLevel"
    nodes = addProperty(prop,nodes)
    g = buildGraph(nodes)   
    # g = buildStudyGraph(nodes) 
    nx.write_graphml(g, "./graphML/test.graphml")
    g = mf.clusterOnNumericPropertyNodes(0.5,g.nodes(),g.edges())
    #g = mf.clusterOnNumericProperty(0.5,g.edges())
    nx.write_graphml(g, "./graphML/test-out.graphml")
