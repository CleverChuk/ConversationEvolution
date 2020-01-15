from collections import defaultdict
from api.mapper import Edge
from api.models import Node, ID
import statistics as stats
from uuid import uuid4

DEFAULT_MEAN = 0.0

class AdjacencyListUnDirected:
    def __init__(self, *edges):  # list of edge object with start_node and end_node properties
        self._list = defaultdict(list)
        self.build(edges)

    def build(self, edges):
        for edge in edges:
            self._list[edge.start_node].append(edge.end_node)
            self._list[edge.end_node].append(edge.start_node)

    def is_connected(self, n1, n2):
        return n2 in self._list[n1] or n1 in self._list[n2]

    def neighbors(self, n0):
        return self._list[n0]

    def vertices(self):
        v = set()
        for nodes in self._list.values():
            v.update(nodes)
        return v


class ClusterUtil:
    count = 0
    @staticmethod
    def connect_clusters(c1, c2, graph):
        for n1 in c1.nodes:
            for n2 in c2.nodes:
                if graph.is_connected(n1, n2):
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

        return cluster_node

    @staticmethod
    def attr_list(obj):
        """
            returns the attribute list of the obj

            @params
                - obj: a class object
        """
        return list(obj.keys())


class Cluster:
    def __init__(self, prop, tol=0.01):  # could use a list for prop to make it general
        self.mean = DEFAULT_MEAN
        self.node = None
        self.has_linked = False
        self.count = 0
        self.nodes = []
        self.tol = tol
        self.prop = prop

    def __count_round(self):
        temp = str(self.tol)
        return len(temp) - temp.find('.')

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

        self.mean = round(total/self.count, self.__count_round())

    def re_init(self):  # reinitialize the cluster for repeat computation
        if len(self.nodes):
            keep = self.nodes.pop(0)  # keep node nearest to mean
            tol = self._dist_mean(keep)

            for node in self.nodes:
                temp = self._dist_mean(node)
                if temp < tol:
                    keep['grouped'] = False
                    keep = node
                    tol = temp
                else:
                    node['grouped'] = False

            # initialize properties
            self.nodes.clear()
            self.nodes.append(keep)
            self.count = 1

    def _dist_mean(self, node):  # could use euclidean distance for multivariable prop
        # calculate the linear distance from mean
        if self.mean == DEFAULT_MEAN:
            return node[self.prop]
        return abs(self.mean - node[self.prop])

    def is_near(self, node):  # check if nide is within cluster distance tolerance
        if self.mean != DEFAULT_MEAN:
            return self._dist_mean(node) <= self.tol
        return True

    def __medain(self):
        vals = [node[self.prop] for node in self.nodes]
        vals.sort()
        if self.count % 2 == 0:
            return (vals[self.count//2]+vals[self.count//2+1])/2
        return vals[self.count//2]

    def dist_from(self, node):
        return self._dist_mean(node)

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

# functions


def score(clusters):
    total = 0
    n = len(clusters)
    for c in clusters:
        total += c.mean

    return round(total / n, 2)


def re_init_clusters(clusters):
    for c in clusters:
        c.re_init()


def k_means(nodes, k, prop='sentiment_score', iter_tol=0.001, cluster_tol=0.001):
    # sensitive to first node picked
    clusters = [Cluster(prop, tol=cluster_tol) for i in range(k)] # could initialize each cluster with a node
    diff = 0
    while True:

        for node in nodes:
            clique = None
            dist_score = float('inf')
            for cluster in clusters:
                temp = cluster.dist_from(node)
                if temp < dist_score:
                    clique = cluster
                    dist_score = temp

            clique.add_to(node)

        if abs(score(clusters) - diff) <= iter_tol:
            break
        else:
            diff = score(clusters)
            re_init_clusters(clusters)

    return clusters
