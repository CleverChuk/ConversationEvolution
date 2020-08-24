# Author: Chukwubuikem Ume-Ugwa
# Purpose: Mapper logic.

from collections import defaultdict, OrderedDict, deque
from math import floor
from uuid import uuid4

from libs.analyzers import SentimentAnalyzer as sa
from libs.graphs import AdjacencyListUnDirected
from libs.models import (Node, TreeNode, Edge)
from libs.utils import ClusterUtil


class Mapper:
    """
        Base class for mapper implementation
        Attributes:
            - data: list of graph edges or node
            - epsilon: sensitivity of overlap between intervals
            - property_key: lens
            - num_interval: number of intervals to split data
    """
    JACCARD_THRESH = 0.1

    def __init__(self, data=None, epsilon=0.5, lens="reading_level", num_interval=3):
        if data is None:
            data = []
        self.data = data
        self.epsilon = epsilon
        self.lens = lens
        self.number_of_interval = num_interval
        # For nodes without property_key as field
        self.heterogeneous_edges = []
        self._average = False  # use to determine how to aggregate cluster nodes- mean or median

    @property
    def average(self):
        return self._average

    @average.setter
    def average(self, value):
        self._average = value

    def connect_cluster(self, clusters):
        """
            creates a graph from the interval clusters
            Nodes are connected if their Jaccard is > 0.1

            @param
                - clusters: a dict w/ key = cluster name and value = list of nodes
        """
        id = 0  # edge id
        new_nodes = {}

        edges = []
        # create cluster node
        for name, cluster in clusters.items():
            new_nodes[name] = ClusterUtil.create_cluster_node(name, self.average, cluster, self.attr_list(cluster[0]))
            new_nodes[name]['radius'] += len(cluster) // 2

        # connect clusters base on node overlap
        names = list(clusters.keys())
        clusters = list(clusters.values())
        n = len(names)

        for i in range(n):
            cluster = set(clusters[i])
            for j in range(i + 1, n):
                nextCluster = set(clusters[j])
                # skip this edge if the Jaccard index is less than 0.1
                j_index = round(self.jeccard_index(cluster, nextCluster), 16)
                if j_index < Mapper.JACCARD_THRESH:
                    continue

                if not cluster.isdisjoint(nextCluster) and new_nodes[names[i]] != new_nodes[names[j]]:
                    edges.append(Edge(new_nodes[names[i]], new_nodes[names[j]], id=id, type=j_index))
                    id += 1

        return edges

    def jeccard_index(self, A, B):
        """
            Calculates the Jaccard index of two sets

        @param A
            - A: a set of nodes
            - B: a set of nodes
        """
        if not isinstance(A, set) or not isinstance(B, set):
            raise TypeError("A and B must sets")

        j = len(A.intersection(B)) / len(A.union(B))

        return j

    def attr_list(self, obj):
        """
            returns the attribute list of the obj

            @params
                - obj: a class object
        """
        return list(obj.keys())

    def edge_mean(self, edge, property_key):
        """
            calculates the average property of a given edge

            @param 
                - edge: graph edge
                - property_key: the node attribute to average
        """

        if len(edge) < 2:
            raise Exception("edge must have at least two nodes")

        p1 = edge.start_node[property_key]
        p2 = edge.end_node[property_key]

        if isinstance(p1, str) or isinstance(p2, str):
            raise TypeError("property_key value must be numeric")

        return round((p1 + p2) / 2, 16)


class EdgeMapper(Mapper):
    """
        Specilization of mapper for working with edge clustering

        Attributes:
            - _cluster: clusters generated
    """

    def __init__(self, edges, clustering_algo, epsilon=0.5, lens="reading_level", num_interval=3):
        self._edges = None
        self.clustering_algo = clustering_algo
        self.adjacency_list = AdjacencyListUnDirected(*edges)

        def filter_homogeneous_edge(edge):
            return edge.start_node['type'] == 'comment' and edge.end_node['type'] == 'comment'

        def filter_heterogeneous_edge(edge):
            return edge.start_node['type'] != 'comment' or edge.end_node['type'] != 'comment'

        self.homogeneous_edges = list(filter(filter_homogeneous_edge, edges))
        # Sort the edges based on the property of interest
        self.homogeneous_edges = sorted(self.homogeneous_edges, key=lambda link: self.edge_mean(link, lens))

        super().__init__(self.homogeneous_edges, epsilon, lens, num_interval)
        self.heterogeneous_edges = list(filter(filter_heterogeneous_edge, edges))

    def graph(self):
        """
            helper function
        """
        intervals = self.create_intervals()
        clusters = self.cluster(intervals)
        self._edges = self.connect_cluster(clusters)

        return self._edges

    def create_intervals(self):
        n = len(self.data)
        intervals = []
        window_size = floor(n / self.number_of_interval)

        if window_size == 0:
            window_size = 1

        for i in range(0, n, window_size):
            intervals.append(self.data[i:i + window_size])

        return intervals

    def cluster(self, intervals):
        """
            cluster nodes base on lens
            @params:
                - interval: List[List]
        """
        clusters = []
        for interval in intervals:
            nodes = ClusterUtil.flatten(interval)
            clusters.extend(self.clustering_algo.cluster(nodes))  # 2 is number of cluster per interval

        return clusters

    def connect_cluster(self, clusters):
        n = len(clusters)
        edge_list = []
        for i in range(n):
            for j in range(i + 1, n):
                edge = ClusterUtil.connect_clusters(clusters[i], clusters[j], self.adjacency_list)
                if edge is not None:
                    edge_list.append(edge)
        return edge_list

    @property
    def edges(self):
        if not self._edges:
            self.graph()

        return self._edges

    def is_connected(self, e1, e2):
        """
        check if two edges are connected
        :param e1:
        :param e2:
        :return: boolean
        """
        start_n1, start_n2 = e1.start_node, e1.end_node
        end_n1, end_n2 = e2.start_node, e2.end_node

        return self.adjacency_list.is_connected(start_n1, end_n1) or \
               self.adjacency_list.is_connected(start_n1, end_n2) or \
               self.adjacency_list.is_connected(start_n2, end_n1) or \
               self.adjacency_list.is_connected(start_n2, end_n2)


class NodeMapper(Mapper):
    """
        Specilization of mapper for working with node clustering
    """

    def __init__(self, edges, data, epsilon=0.5, lens="reading_level", num_interval=3):
        self.edges = edges
        super().__init__(data, epsilon, lens, num_interval)

    def cluster_groups(self):
        """
            helper function
        """
        groups = self.create_intervals()
        cluster = self.cluster(groups)

        return self.connect_cluster(cluster)

    def create_intervals(self):
        """
            splits the nodes into intervals based on property_key
        """
        n = len(self.data)
        incr_size = floor(n / self.number_of_interval)
        if incr_size == 0:
            incr_size = 1

        intervals = []
        # create the intervals using property_key value to mark the range bounds
        for i in range(0, n, incr_size):
            n = self.data[i:i + incr_size]
            intervals.append(n)

        groups = defaultdict(list)  # map to hold groups
        length = len(intervals)

        for i in range(length - 1):
            next = i + 1
            minimum = intervals[i][0][self.lens] - self.epsilon
            maximum = intervals[i][-1][self.lens] + self.epsilon

            # find overlaps
            for j in range(next, len(self.data)):
                if self.data[j][self.lens] <= maximum and self.data[j] not in intervals[i]:
                    intervals[i].append(self.data[j])

            groups[(minimum, maximum)] = intervals[i]

            # make sure to include the last interval in the group map
            if next == length - 1:
                minimum = intervals[next][0][self.lens] - self.epsilon
                maximum = intervals[next][-1][self.lens] + self.epsilon

                for n in intervals[i]:
                    if n[self.lens] <= maximum and n not in intervals[next]:
                        intervals[next].append(n)
                groups[(minimum, maximum)] = intervals[next]

        return groups

    def cluster(self, groups):
        """
            cluster nodes base on their connection with each other
            @params:
                - groups: dict of edges
        """
        clusters = OrderedDict()
        clusterId = 0

        for group in groups.values():
            for node in group:
                if clusterId not in clusters:
                    clusters[clusterId] = []
                    clusters[clusterId].append(node)

                # add nodes with edges in the same cluster
                for edge in self.edges:
                    if edge[0].id_0 == node.id_0 and edge[1] in group and edge[1] not in clusters[clusterId]:
                        clusters[clusterId].append(edge[1])

                    elif edge[1].id_0 == node.id_0 and edge[0] in group and edge[0] not in clusters[clusterId]:
                        clusters[clusterId].append(edge[0])

                clusterId += 1

        temp = list(clusters.keys())
        indices = []
        # find the index duplicate clusters
        for i in temp:
            s1 = set(clusters[i])
            for j in temp[i + 1:]:
                s2 = set(clusters[j])
                if s2 == s1:
                    indices.append(j)

        # remove duplicate clusters
        for i in indices:
            clusters.pop(i, "d")
        return clusters


class TreeMapper:
    """
        A mapper implementation for working with dendogram
        Attributes:
            - _cluster: clusters generated
            - intervals: intervals generated
    """

    def __init__(self):
        """
            Initializes the TreeMapper object with tree root and filter function
        """
        self._cluster = []
        self.intervals = defaultdict(list)

    @property
    def cluster(self):
        return self._cluster

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        if not value:
            raise ValueError()

        self._root = value

    def _map(self, parent_id, children, filter_function):
        """
            Map the children of a node using the filter function.
            Cluster them based on the mapped value
            @params:
                - parent_id: id of parent node
                - children: list of child nodes
                - filter_function: filter function
        """
        cluster = defaultdict(list)

        # Use the filter function to calculate a mapping for the children
        for child in children:
            value = filter_function(child)
            cluster[value].append(child)

        # Cluster the nodes based on their filter function value
        for value, array in cluster.items():
            node = Node()
            node["composition"] = []
            node["parent_id"] = parent_id
            node["value"] = value
            node["type"] = "mapper"
            node["id"] = uuid4()

            for child in array:
                node["composition"].append(child["id"])

            self._cluster.append(node)

    def bfs(self, root, filter_function=lambda node: sa.convert_score(sa.get_sentiment(node["body"]))):
        """
            Use BFS to visit all nodes in the tree in level order traversal
            @params:
                - root: root node
                -filter_function: filter function
        """
        queue = deque()
        queue.append(root)

        while queue:
            root = queue.popleft()
            if root["children"] is None:
                continue
            # can map level by level by storing children list then mapping the whole level
            # instead of doing children mapping
            self._map(root["id"], root["children"], filter_function)
            for child in root["children"]:
                queue.append(child)

    def make_tree(self, root, nodes, visited=None):
        """
            Create a tree rooted at root
            @params:
                - root: tree root
                - nodes: list of nodes
                - visited: visited list to avoid infinite loop
        """
        if visited is None:
            visited = []

        for child in nodes:
            if child["parent_id"] == root["id"] or (root["composition"] and child["parent_id"] in root["composition"]) \
                    or (child['type'] == 'article' and child['subreddit'] == root[
                'id']):  # added this line in order to be able to create a tree for an entire subreddit
                if "children" in root:
                    root["children"].append(child)
                else:
                    root["children"] = [child]

                if child not in visited:
                    visited.append(child)
                    # Traverse only if reachable from root
                    self.make_tree(child, nodes, visited)

        return root

    def map(self, interval, filter_function):
        """
            Map the interval of nodes using the filter function.
            Cluster them based on the mapped value
            @params:
                - interval: list of nodes
                - filter_function: filter function
        """
        cluster = defaultdict(list)

        # Use the filter function to calculate a mapping for the interval
        for node in interval:
            value = filter_function(node)
            cluster[value].append(node)

        # Cluster the nodes based on their filter function value
        for value, array in cluster.items():
            node = Node()
            node["composition"] = []
            node["value"] = value
            node["type"] = "mapper"
            node["id"] = uuid4()

            # use the parent id the node with the minimum depth as parent id for the mapper node
            min_depth = float('inf')
            parent_id = None

            for child in array:
                node["composition"].append(child["id"])
                if child['depth'] < min_depth:
                    min_depth = child['depth']
                    parent_id = child["parent_id"]

            node["parent_id"] = parent_id

            self._cluster.append(node)

    def _populate_intervals(self, root, intervals):
        """
            add nodes to intervals based on their depth
            @params:
                - root: parent node
                - interval: list of intervals
        """
        if root["parent_id"]:
            depth = root["depth"]
            for pair in intervals:
                low, high = pair
                if low <= depth <= high:
                    self.intervals[pair].append(root)
                    break

        if root["children"]:
            for child in root["children"]:
                self._populate_intervals(child, intervals)

    def _cluster_interval(self, filter_function):
        """
            Cluster nodes in each interval using filter_function
            @param:
                - filter_functon: filter function
        """
        for nodes in self.intervals.values():
            self.map(nodes, filter_function)

    def execute(self, root, interval=[], epsilon=0.001, filter_function=lambda node: sa.get_sentiment(node["body"])):
        """
            Start execution of the algorithm
            @params:
                - root: root node
                - interval: list of intervals. can also be int
        """
        del self._cluster[:]
        if type(interval) == int:
            interval = self._generate_intervals(self.tree_height(root), interval)
        # add the depth of the nodes as a property
        self._add_depth(root)
        # create intervals
        self._populate_intervals(root, interval)
        # cluster intervals        
        # self._clusterInterval(filterFunction)
        self.cluster_by_connectedness(epsilon, filter_function)

        return self._cluster

    def _generate_intervals(self, height, count):
        """
            Create intervals base on tree height
            @params:
                - height: height of tree
                - count: number of intervals
        """
        intervals = []
        n = height // count

        i = 1
        while i <= height:
            intervals.append((i, i + n))
            i = i + n + 1

        return intervals

    def tree_height(self, root):
        """
            Calculate the height of a tree
            @params:
                - root: tree root
        """
        if not root["children"]:
            return 0

        height = 0
        for child in root["children"]:
            height = max(height, self.tree_height(child) + 1)

        return height

    def _add_depth(self, root, depth=0):
        """
            Label each node with its depth
            @params:
                - root: node
                - depth: depth of root
        """
        root["depth"] = depth
        if root["children"]:
            for child in root["children"]:
                self._add_depth(child, depth + 1)

    def cluster_by_connectedness(self, epsilon, filter_function):
        """
            Cluster nodes based on their connectedness
            @params:
                - epsilon: filter_function value threshold
                - filter_function: filter function/lens
        """
        mapper_nodes = []
        for interval in self.intervals.values():
            cluster = defaultdict(list)
            n = len(interval)

            if n > 1:
                for i in range(n):
                    if not interval[i]['isClustered']:
                        cluster[interval[i]] = [interval[i]]
                        for j in range(i + 1, n):
                            if self.is_child_of(cluster[interval[i]][-1], interval[j]) and \
                                    abs(filter_function(interval[i]) - filter_function(interval[j])) <= epsilon:
                                cluster[interval[i]].append(interval[j])
                                interval[j]['isClustered'] = True
                                # print("first: {0} |  second: {1}".format(interval[i], interval[j]))

            else:
                cluster[interval[0]].append(interval[0])

            # mapper_nodes.extend(cluster.keys())
            for node, nodeSet in cluster.items():
                node["composition"] = [n["id"] for n in nodeSet if n["id"] != node["id"]]
                node["radius"] = 3.14 * (len(nodeSet) / 2 + 1) ** 2
                mapper_nodes.append(node)

        # work around for python object reference mess
        for node in mapper_nodes:
            mapper_node = TreeNode(node["id"], type="mapper")
            mapper_node["radius"] = node["radius"]
            mapper_node["parent_id"] = node["parent_id"]
            mapper_node['value'] = filter_function(node)
            mapper_node['composition'] = node["composition"]
            self._cluster.append(mapper_node)

    def is_child_of(self, parent, child):
        """
            Return whether there is a parent-child relationship
            @params:
                - parent: parent node
                - child: child node
        """
        if parent["children"]:
            for node in parent["children"]:
                if node["id"] == child["id"]:
                    return True

        return False

    def top_sort(self, graph):
        """
            Sort nodes in topological order
            @params:
                - graph: graph
        """
        sorted_nodes, visited = deque(), set()
        for node in graph:
            self.dfs(graph, node, visited, sorted_nodes)

        return list(sorted_nodes)

    def dfs(self, graph, start_node, visited, sorted_nodes):
        """
            Traverse the graph using dfs used in conjunction with top_sort
            @params:
                - graph: graph
                - start_node: start
                - visited: visited list
                - sorted_nodes: result list
        """
        visited.add(start_node)
        if start_node["children"]:
            neighbors = [child for child in start_node["children"] if child in graph]
            for neighbor in neighbors:
                if neighbor not in visited:
                    self.dfs(graph, neighbor, visited, sorted_nodes)
        sorted_nodes.append(start_node)
