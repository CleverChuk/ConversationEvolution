from collections import defaultdict
from libs.models import Node, Edge
from math import sqrt, ceil
from libs.utils import ClusterUtil
import random
from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
import igraph
from py2neo import Relationship

random.seed(0)
class SKLearnKMeans(KMeans):
    def __init__(self, n_clusters = 8):
        self.vect = DictVectorizer()
        super().__init__(n_clusters=n_clusters)
        
    def fit(self, X):
        _X = self.vect.fit_transform(X)
        return super().fit(_X)

    def transform_node(self, node):
        return self.vect.transform(node)

class IGraph(igraph.Graph):
    def __init__(self):
        self.mapping = {}
        super().__init__()
    
    def create_mapping(self, edges):
        temp_set = set()
        for edge in edges:
            temp_set.add(edge.start_node)
            temp_set.add(edge.end_node)

        for i, node in enumerate(temp_set):
            self.mapping[node] = i
        
        return self.mapping

    def transform(self, edges_list, mapping):
        temp = []
        for edge in edges_list:
            start_node, end_node = edge.start_node, edge.end_node
            temp.append((mapping[start_node], mapping[end_node]))

        return temp
    
    def add_edges(self, edge_list):
        if not isinstance(edge_list, list):
            raise Exception(f"Expected a list, but got -> {str(edge_list)}")

        if not len(edge_list):
            raise Exception(f"Expected a non-empty list, but got an empty list")

        if not isinstance(edge_list[0], Relationship):
            raise Exception(f"Expected a list of {str(Relationship)}, but got a list of {str(edge_list[0])}")

        self.create_mapping(edge_list)
        self.add_vertices(len(self.mapping))
        super().add_edges(self.transform(edge_list, self.mapping))

    def transform_layout_for_drawing(self, layout):
        json = {"coords":layout.coords}
        links = []
        
        for edge in self.es:
            links.append({"source": edge.source, "target": edge.target})
        json["links"] = links

        nodes = [None]*len(self.mapping)
        for node, i in self.mapping.items():
            nodes[i] = node
        
        json["nodes"] = nodes

        return json


class AdjacencyListUnDirected:
    def __init__(self, *edges):  # list of edge object with start_node and end_node properties
        self.__list = defaultdict(list)
        self.build(edges)

    @property
    def alist(self):
        return self.__list

    def build(self, edges):
        for edge in edges:
            s = edge.start_node
            d = edge.end_node
            if s['id'] != d['id']:  # eliminate self loops and force property download from neo4j
                s = Node(dict(s))
                d = Node(dict(d))
                self.__list[s].append(d)
                self.__list[d].append(s)

    def is_connected(self, n1, n2):
        return n2 in self.__list[n1] or n1 in self.__list[n2]

    def neighbors(self, n0):
        return self.__list[n0]

    def vertices(self):
        return list(self.__list.keys())


class Cluster:
    def __init__(self, prop = "reading_level", node = None, tol=0.01):  # could use a list for prop to make it general
        self.mean = 0 if node is None else node[prop]
        self.node = None  # store node representation of the cluster
        self.has_linked = False
        self.count = 1
        self.nodes = [] if node is None else [node]
        self.tol = tol
        self.prop = prop
        self.component_id = random.randint(0, 400000000) if node is None else node['component_id']

    def add_to(self, node):
        if not node['grouped']:
            self.count += 1
            node['grouped'] = True
            self.nodes.append(node)
            self._update_mean()

    def add_node(self, node):
        self.nodes.append(node)

    def _update_mean(self):
        total = 0
        for node in self.nodes:
            total += node[self.prop]

        self.mean = round(total/self.count,
                          ClusterUtil.count_decimal_places(self.tol))

    def re_init(self):  # reinitialize the cluster for repeat computation
        if len(self.nodes):
            keep = self.nodes.pop(0)
            tol = self._distance_metric(keep)

            for node in self.nodes:
                temp = self._distance_metric(node)
                if temp < tol:  # keep node nearest to mean
                    keep['grouped'] = False
                    keep = node
                    tol = temp
                else:
                    node['grouped'] = False

            # initialize properties
            self.nodes.clear()
            self.nodes.append(keep)
            self.count = 1

    def is_empty(self):
        return not len(self.nodes)

    # could use euclidean distance for multivariable prop
    def _distance_metric(self, node):
        # calculate the Euclidean distance
        if self.is_empty():
            return node[self.prop]  # return value for node if cluster is empty
        return sqrt(pow(self.mean - node[self.prop], 2))

    def is_reachable(self, node):  # check if node is in the same components
        if self.is_empty():
            return True
        return self.component_id == node["component_id"]

    def __medain(self):
        vals = [node[self.prop] for node in self.nodes]
        vals.sort()
        if self.count % 2 == 0:
            return (vals[self.count//2]+vals[self.count//2+1])/2
        
        return vals[self.count//2]

    def dist_from(self, node):
        return self._distance_metric(node)

    def is_related(self, cluster, graph):  # connect related clusters
        for n1 in cluster.nodes:
            for n2 in self.nodes:
                if graph.is_connected(n1, n2):
                    return True
        return False

    def to_node(self, aggregate_by='mean'):
        if self.count and self.node is None:
            self.node = ClusterUtil.create_cluster_node('mapper', aggregate_by, self.nodes,
                                                        ClusterUtil.attr_list(self.nodes[0]))

        return self.node

    def __eq__(self, c):
        if isinstance(c, Cluster):
            return self.component_id == c.component_id
        return False

# functions

def score(clusters, tol):
    total = 0
    n = len(clusters)
    for c in clusters:
        total += c.mean

    return round(total / n, ClusterUtil.count_decimal_places(tol))


def re_init_clusters(clusters):
    for c in clusters:
        c.re_init()


def k_means(nodes, k, prop='sentiment_score', iter_tol=0.001, cluster_tol=0.001):
    # sensitive to first node picked
    N = len(nodes)
    if k > N:
        k = ceil(N / 2)

    init_nodes = random.choices(nodes, k=k)
    for node in init_nodes:
        node['grouped'] = True

    clusters = [Cluster(prop, init_nodes[i], tol=cluster_tol)
                for i in range(k)]  # could initialize each cluster with a node
    diff = 0
    while True:
        for node in nodes:
            closest_cluster = None
            dist_score = float('inf')
            for cluster in clusters:
                temp = cluster.dist_from(node)
                if temp < dist_score:
                    closest_cluster = cluster
                    dist_score = temp

            if closest_cluster.is_reachable(node):
                closest_cluster.add_to(node)

        if abs(score(clusters, iter_tol) - diff) <= iter_tol:
            break
        else:
            diff = score(clusters, iter_tol)
            re_init_clusters(clusters)

    return clusters
