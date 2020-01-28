from collections import defaultdict
from libs.mapper import Edge
from libs.models import Node, ID
import statistics as stats
from uuid import uuid4
from math import sqrt, ceil
import random

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
            if  s['id'] != d['id']: # eliminate self loops and force property download from neo4j
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



class ClusterUtil:
    count = 0
    @staticmethod
    def connect_clusters(c1, c2, graph):
        if c1 == c2:
            for n1 in c1.nodes:
                for n2 in c2.nodes:
                    if graph.is_connected(n1,n2):
                        node1 = c1.to_node()
                        node2 = c2.to_node()
                        c1.has_linked = c2.has_linked = True
                        return Edge(node1, node2)

    @staticmethod
    def create_cluster_node(name, agg,  cluster, property_keys):
        """
            calculates the average of all the properties in property_key for
            all the clusters in cluster
            creates a node with the average(numeric) or mode(string) attribute for a cluster

            @param
                - name: cluster name
                - cluster: list of nodes
                - property_keys: list of node attribute
        """

        def create_compositions(cluster_node, node):
            # Node composition of this cluster node used to highlighted nodes in the
            # front-end visualization
            if cluster_node['composition'] and node["id"] in cluster_node['composition']:
                return

            if cluster_node['composition']:
                cluster_node['composition'].append(node['id'])

            else:
                cluster_node['composition'] = [node['id']]

        if not isinstance(cluster, list) and not isinstance(property_keys, list):
            raise Exception("cluster and property_keys must be lists")

        numerical_variables = []
        cluster_node = Node({'name': name})
        category_variable = defaultdict(int)

        mode_value = 0
        mode_var = None
        for property_key in property_keys:
            for node in cluster:
                create_compositions(cluster_node, node)
                tp = node[property_key]
                if isinstance(tp, str):  # use mode for categorical variables
                    category_variable[tp] += 1
                    if category_variable[tp] > mode_value:
                        mode_value = category_variable[tp]
                        mode_var = tp
                else:
                    numerical_variables.append(tp)

            if len(numerical_variables):  # use median for numerical variables
                if agg == "mean":
                    cluster_node[property_key] = float(
                        round(stats.mean(numerical_variables), 4))
                    numerical_variables.clear()
                else:
                    numerical_variables.sort()
                    cluster_node[property_key] = float(
                        round(stats.median(numerical_variables), 4))
                    numerical_variables.clear()

            else:
                cluster_node[property_key] = str(mode_var)
                mode_value = 0
                category_variable.clear()

        cluster_node["id"] = uuid4()
        cluster_node.pop("body",None)
        nodes = cluster_node.pop('composition',[])
        cluster_node['node_count'] = len(nodes)
        return cluster_node

    @staticmethod
    def attr_list(obj):
        """
            returns the attribute list of the obj

            @params
                - obj: dict object
        """
        return list(obj.keys())

    @staticmethod
    def count_decimal_places(tol):
        temp = str(tol)
        return len(temp) - temp.find('.')

    @staticmethod
    def label_components(graph):
        visited = set()
        components = defaultdict(list)
        def dfs(v, id):
            if v not in visited:
                visited.add(v)
                if v in graph:
                    for u in graph[v]:
                        dfs(u, id)
                components[id].append(v)
                v["component_id"] = id
        
        id = 0
        for node in graph:
            dfs(node, id)
            id += 1
        
        return components


class Cluster:
    def __init__(self, prop, n, tol=0.01):  # could use a list for prop to make it general
        self.mean = n[prop]
        self.node = None # store node representation of the cluster
        self.has_linked = False
        self.count = 1
        self.nodes = [n]
        self.tol = tol
        self.prop = prop
        self.component_id = n['component_id']

    def add_to(self, node):
        if not node['grouped']:
            self.count += 1
            node['grouped'] = True
            self.nodes.append(node)
            self._update_mean()

    def _update_mean(self):
        total = 0
        for node in self.nodes:
            total += node[self.prop]

        self.mean = round(total/self.count, ClusterUtil.count_decimal_places(self.tol))

    def re_init(self):  # reinitialize the cluster for repeat computation
        if len(self.nodes):
            keep = self.nodes.pop(0)  
            tol = self._distance_metric(keep)

            for node in self.nodes:
                temp = self._distance_metric(node)
                if temp < tol: # keep node nearest to mean
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

    def _distance_metric(self, node):  # could use euclidean distance for multivariable prop
        # calculate the Euclidean distance
        if self.is_empty():
            return node[self.prop] # return value for node if cluster is empty
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

    clusters = [Cluster(prop, init_nodes[i], tol=cluster_tol) for i in range(k)] # could initialize each cluster with a node
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
