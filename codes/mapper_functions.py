from collections import defaultdict
from models import Node, Comment
import networkx as nx
import random


def time(g, nodes):
    """
    :type g: int

    :type nodes: List[Node]

    :rtype: graph 
    """
    nodes = sorted(nodes, key=lambda n: n.timestamp)
    iw = g * nodes[0].timestamp  # calculate the interval width
    h = nodes[-1].timestamp  # get upperbound
    l = nodes[0].timestamp  # get lowerbound

    groups = defaultdict(list)  # map to hold groups
    end = l+iw

    while l < (h+iw):
        pair = (time_string(l), time_string(end))
        pair = (l, end)

        for node in nodes:
            if l <= node.timestamp and node.timestamp <= end:
                groups[pair].append(node)

        l = end
        end += iw

    result = list()
    for k, v in groups.items():
        result.append((k, {"count": len(v)}))

    return result


def reading_level(gain, nodes):
    """
    :type gain: int

    :type nodes: List[Node]

    :rtype: graph 
    """
    nodes = sorted(nodes, key=lambda n: n.readingLevel)
    # calculate the interval width
    iw = int(gain * random.choice(nodes).readingLevel)
    h = int(nodes[-1].readingLevel)  # get upperbound
    l = int(nodes[0].readingLevel)  # get lowerbound

    groups = defaultdict(list)  # map to hold groups
    end = l+iw

    while l < (h+iw):
        pair = (l, end)

        for node in nodes:
            if l <= node.readingLevel and node.readingLevel <= end:
                groups[pair].append(node)

        l = end
        end += iw

    result = list()

    for k, v in groups.items():
        result.append((k, {"count": len(v)}))

    return result


def graphFromGroup(groups):
    """
        :type groups :List

        :rtype graph
    """
    g = nx.DiGraph()
    n = len(groups) - 1

    for i in range(n):
        n, d = groups[i]
        g.add_node(n, count=d["count"])
        g.add_edge(groups[i][0], groups[i+1][0])

    g.add_edge(groups[0][0], groups[-1][0])

    return g


def time_string(t):
    """
        :type t: long

        :rtype string: date
    """
    import time
    import datetime
    t = datetime.date.fromtimestamp(t).timetuple()
    return time.strftime("%Y-%m-%d", t)
