from collections import defaultdict
from models import Comment, Node
import networkx as nx
import random
from math import ceil, floor


def time(g, edges):
    """
    :type g: int

    :type edges: List[edge]

    :rtype: graph 
    """
    edges = sorted(edges, key=lambda n: n.timestamp)
    iw = g * edges[0].timestamp  # calculate the interval width
    h = edges[-1].timestamp  # get upperbound
    l = edges[0].timestamp  # get lowerbound

    groups = defaultdict(list)  # map to hold groups
    end = l+iw

    while l < (h+iw):
        pair = (time_string(l), time_string(end))
        pair = (l, end)

        for edge in edges:
            if l <= edge.timestamp and edge.timestamp <= end:
                groups[pair].append(edge)

        l = end
        end += iw

    result = list()
    for k, v in groups.items():
        result.append((k, {"count": len(v)}))

    return result


def clusterOnNumericProperty(shift, edges, prop="readingLevel"):
    groups = numeric_interval(shift, edges,prop)
    cluster = clusterInterval(groups)

    return graphFromCluster(cluster,prop)


def numeric_interval(shift, edges, prop):
    """
        splits the edges into 3 intervals based on reading level property

        :type shift: int

        :type edges: List[edge]

        :rtype: dict 
    """
    edges = sorted(edges, key=lambda e: (
        e[0].__dict__[prop] + e[1].__dict__[prop])/2)
    n = len(edges)
    median = getAverage(edges[n//2], prop) if n % 2 == 1 else (getAverage(
        edges[n//2], prop) + getAverage(edges[n//2+1], prop))/2

    fi = (getAverage(edges[0], prop), median) # first interval
    si = (median, getAverage(edges[-1], prop))  # second interval
    ti = (median-shift, median+shift)  # third interval

    groups = defaultdict(list)  # map to hold groups

    for pair in (fi, si, ti):
        for edge in edges:
            avg = getAverage(edge, prop)
            if pair[0] <= avg and avg <= pair[1]:
                groups[pair].append(edge)
  
    return groups


def clusterInterval(groups):
    """
        cluster nodes base on there connection with each other

        :type groups: dict

        :rtype clusters: dict
    """
    clusters = defaultdict(list)
    cluster = 0

    for e_List in groups.values():
        for i in range(len(e_List)):                              
            clusters[cluster].append(e_List[i][0])
            clusters[cluster].append(e_List[i][1])

            for edge in e_List:
                if edge[0] in clusters[cluster] and edge[1] not in clusters[cluster]:
                    clusters[cluster].append(edge[1])

                elif edge[1] in clusters[cluster] and edge[0] not in clusters[cluster]:
                    clusters[cluster].append(edge[0])

            cluster += 1

    n = len(clusters)
    indices = []
    # find the index duplicate clusters
    for i in range(n):
        s1 = set(clusters[i])
        for j in range(i+1,n):
            s2 = set(clusters[j])
            s3 = s1.intersection(s2)
            if len(s3) == len(s1):
                indices.append(j)
    
    # remove duplicate clusters
    for i in indices:
        clusters.pop(i,"d")

    return clusters

def graphFromCluster(clusters,prop):
    """
        this functions creates a graph from the interval
        clusters.

        :type cluster :dict

        :rtype graph
    """
    g = nx.DiGraph()
    newNodes = {}

    for name, cluster in clusters.items():
        newNodes[name] = clusterAverage(name, cluster, getProperties(cluster[0]))
  
    for name, cluster in clusters.items():
        for node in cluster:
            for n, c in clusters.items():
                if g.has_edge(newNodes[n], newNodes[name]) or name == n:
                    continue

                if node in c:
                    g.add_edge(newNodes[name], newNodes[n],
                               name=prop.upper())
    
    for node in newNodes.values():
        g.add_nodes_from([(node, node.__dict__)])

    return g

def getProperties(obj):
    """
        returns the property list of the obj

        :type obj : class object

        :rtype list 
    """
    return list(obj.__dict__.keys())


def clusterAverage(name, cluster, props):
    """
        calculates the average of all the properties in prop for
        all the clusters in cluster

        creates a node based on these properties

        :type name: string
        :type cluster : list
        :type props : list

        :rtype Node
    """
    if not isinstance(cluster, list) and not isinstance(props, list):
        raise Exception("cluster and props must be lists")

    rsum = 0
    n = len(cluster)
    clusterNode = Node(name)

    for prop in props:
        for node in cluster:
            tp = node.__dict__[prop]
            if isinstance(tp, str):
                break

            rsum += tp

        if rsum != 0:
            clusterNode.__dict__[prop] = rsum/n
            rsum = 0

    return clusterNode


def getNodes(groups):
    """
        creates a node from average properties of an 
        edge

        returns a list of generated nodes

        :type groups: dict

        :rtype List: Node
    """

    item = groups.popitem()
    groups[item[0]] = item[1]

    edges = item[1]
    node = edges[0][0]
    nodes = []

    node_props = node.__dict__.keys()

    for k, v in groups.items():
        for edge in v:
            for n in edge:
                if isinstance(n, Node):
                    newNode = Node(k)
                    for prop in node_props:
                        newNode.__dict__[prop] = getAverage(edge, prop)
                    nodes.append(newNode)

    return nodes


def getAverage(edge, prop):
    """
        calculates the average property of a given edge

        :type edge: tuple
        :type prop: string

        :rtype mean(prop)
    """

    if len(edge) < 2:
        raise Exception("edge must have at least two nodes")

    p1 = edge[0].__dict__[prop]
    p2 = edge[1].__dict__[prop]

    # print("Edge:%s val:%d|Edge:%s val:%d"%(edge[0],p1,edge[1],p2))

    return round((p1+p2)/2,2)

def time_string(t):
    """
        time formatting

        :type t: long

        :rtype string: date
    """
    import time
    import datetime
    t = datetime.date.fromtimestamp(t).timetuple()
    return time.strftime("%Y-%m-%d", t)
