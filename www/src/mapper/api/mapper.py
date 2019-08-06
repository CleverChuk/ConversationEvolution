# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to map the main to a subgraph that approximates the main graph.
#          It is important to know that the mapper functions
#          assumes that the nodes given to it are of the same Type.

import statistics as stats
from collections import defaultdict, OrderedDict, deque
from math import floor
from libs.codes.analyzers import SentimentAnalyzer as sa
from .models import Node
from uuid import uuid4

"""
@param 
    :type 
    :description:
"""


class Edge:
    def __init__(self, src, dest, **properties):
        # coarse py2neo to download all fields
        src['name'], dest['name']
        self.start_node = src
        self.end_node = dest
        self.properties = properties
        self._index = -1

    @classmethod
    def cast(self, py2neo_rel):
        return self(py2neo_rel.start_node, py2neo_rel.end_node)

    def __getitem__(self, key):
        if key == 0:
            return self.start_node
        elif key == 1:
            return self.end_node
        elif key == 2:
            return self.properties
        else:
            return None

    def __len__(self):
        return 3

    def __repr__(self):
        return self.start_node['type'] + "->" + self.end_node['type']


class Mapper:
    JACCARD_THRESH = 0.1

    def __init__(self, data=[], epsilon=0.5, property_key="reading_level", num_interval=3):
        self.data = data
        self.epsilon = epsilon
        self.property_key = property_key
        self.num_interval = num_interval
        # For nodes without property_key as field
        self.filtered_in_data = []
        self._average = False  # use to determine how to aggregate cluster nodes- mean or median

    @property
    def average(self):
        return self._average

    @average.setter
    def average(self, value):
        self._average = value

    def graph_cluster(self, clusters):
        """
            creates a graph from the interval clusters
            Nodes are connected if their Jaccard is > 0.1

            @param clusters
                :type dict
                :description: a dict w/ key = cluster name and value = list of nodes
            :rtype tuple of graph and list of edges
        """
        id = 0  # edge id
        new_nodes = {}

        edges = []
        # create cluster node
        for name, cluster in clusters.items():
            new_nodes[name] = self.create_cluster_node(name, cluster, self.attr_list(cluster[0]))
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
                j_index = round(self.jeccard_index(cluster, nextCluster), 2)
                if j_index < Mapper.JACCARD_THRESH:
                    continue

                if not cluster.isdisjoint(nextCluster) and new_nodes[names[i]] != new_nodes[names[j]]:
                    edges.append(Edge(new_nodes[names[i]], new_nodes[names[j]], id=id, type=j_index)) 
                    id += 1

        # assumes filtered is always of type author and sentiment
        # authors = []
        # sentiments = []
        # # #TODO: add if statement to ignore or perform this task
        # for link in self.filtered_in_data:
        #     if link[0]['type'] == 'author':
        #         authors.append(link[0])

        #     #     elif link[0]['type'] == 'sentiment':
        #     #         sentiments.append(link[0])

        #     if link[1]['type'] == 'author':
        #         authors.append(link[1])
        #     elif link[1]['type'] == 'sentiment':
        #         sentiments.append(link[1])

        # N = len(edges)
        # #TODO: add if statement to ignore or perform this task

        # for i in range(N):
        #     for node in authors:
        #         # check if the author's comment contributed to this cluster
        #         if edges[i][0]['authors']:
        #             a = edges[i][0]['authors'].get(node['name'])
        #             if a != None:
        #                 edges.append(Edge(node, edges[i][0]))
        #                 # Remove author to avoid creating multiple author edges to all contributing nodes
        #                 del edges[i][0]['authors'][a]

        #         if edges[i][1]['authors']:
        #             a = edges[i][1]['authors'].get(node['name'])
        #             if a != None:
        #                 edges.append(Edge(node, edges[i][1]))
        #                 # Remove author to avoid creating multiple author edges to all contributing nodes
        #                 del edges[i][1]['authors'][a]

        # #TODO: add if statement to ignore or perform this task
        # for node in sentiments:
        #     for i in range(N):
        #         # connect this cluster to its overall sentiment
        #         if node['name'] == edges[i][0]['sentiment']:
        #             edges.append(Edge(edges[i][0], node))

        #         if node['name'] == edges[i][1]['sentiment']:
        #             edges.append(Edge(edges[i][1], node))

        return edges

    def jeccard_index(self, A, B):
        """
            Calculates the Jaccard index of two sets

        @param A
            :type set
            :description: a set of nodes

        @param B
            :type set 
            :description: a set of nodes
        """
        if not isinstance(A, set) or not isinstance(B, set):
            raise TypeError("A and B must sets")

        j = len(A.intersection(B)) / len(A.union(B))

        return j

    def attr_list(self, obj):
        """
            returns the property list of the obj

            @param obj
                :type type
                :description: a class object

            :rtype list 
        """
        return list(obj.keys())

    def create_cluster_node(self, name, cluster, property_keys):
        """
            calculates the average of all the properties in property_key for
            all the clusters in cluster
            creates a node with the average(numeric) or mode(string) attribute for a cluster

            @param name
                :type string
                :description: cluster name

            @param cluster
                :type list
                :description: list of nodes

            @param property_keys
                :type list
                :description: list of node attributes

            :rtype Node
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

            # add authors dictionary to cluster use to form edge
            # if cluster_node['authors']:
            #     cluster_node['authors'].append(node['author'])

            # else:
            #     cluster_node['authors'] = [node['author']]
                
                    
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

            if len(numerical_variables) != 0:  # use median for numerical variables
                if self._average:
                    cluster_node[property_key] = float(
                        round(stats.mean(numerical_variables), 4))
                    numerical_variables.clear()
                else:
                    numerical_variables = sorted(numerical_variables)
                    cluster_node[property_key] = float(
                        round(stats.median(numerical_variables), 4))
                    numerical_variables.clear()

            else:
                cluster_node[property_key] = str(mode_var)
                mode_value = 0
                category_variable.clear()

        cluster_node["id"] = uuid4()
        
        return cluster_node

    def edge_mean(self, edge, property_key):
        """
            calculates the average property of a given edge

            @param edge
                :type tuple
                :description: graph edge

            @param property_key
                :type string
                :description: the node attribute to average

            :rtype mean(property_key)
        """

        if len(edge) < 2:
            raise Exception("edge must have at least two nodes")

        p1 = edge.start_node[property_key]
        p2 = edge.end_node[property_key]
        
        if isinstance(p1, str) or isinstance(p2, str):
            raise TypeError("property_key value must be numeric")

        return round((p1 + p2) / 2, 2)

class EdgeMapper(Mapper):
    def __init__(self, edges, epsilon=0.5, property_key="reading_level", num_interval=3):
        self._cluster = None
        def filter_out(edge):
            return edge.start_node['type'] == 'comment' and edge.end_node['type'] == 'comment'

        def filter_in(edge):
            return edge.start_node['type'] != 'comment' or edge.end_node['type'] != 'comment'

        self.filtered_data = list(filter(filter_out, edges))
        # Sort the edges based on the property of interest
        self.filtered_data = sorted(self.filtered_data, key=lambda link: self.edge_mean(link, property_key))

        super().__init__(self.filtered_data, epsilon, property_key, num_interval)
        self.filtered_in_data = list(filter(filter_in, edges))

    def graph(self):
        """
            wrapper function
        """
        groups = self.create_intervals()
        cluster = self.cluster_groups(groups)
        self._cluster = self.graph_cluster(cluster)
        
        return self._cluster

    def create_intervals(self):
        """
            splits the edges into intervals based on property_key

            @param epsilon
                :type float
                :description: specifies how much to shift the interval to create overlap

            @param edges
                :type list
                :description: list of edges

            @param property_key
                :type string
                :description: the node property used to create interval

            @param num_intervals
                :type int
                :description: number of intervals to create

            :rtype: dict 
        """
        n = len(self.data)
        intervals = []
        incr_size = floor(n / self.num_interval)

        if incr_size == 0:
            incr_size = 1

        # create the intervals using property value to mark the range bounds
        for i in range(0, n, incr_size):
            intervals.append(self.data[i:i + incr_size])

        groups = defaultdict(list)  # map to hold groups
        length = len(intervals)
        for i in range(length - 1):
            next = i + 1

            # adjust the overlap range by epsilon
            minimum = self.edge_mean(
                intervals[i][0], self.property_key) - self.epsilon
            maximum = self.edge_mean(
                intervals[i][-1], self.property_key) + self.epsilon

            # create the overlap between interval i and i+1
            for e in intervals[next]:
                if self.edge_mean(e, self.property_key) <= maximum and e not in intervals[i]:
                    intervals[i].append(e)

            groups[(minimum, maximum)] = intervals[i]

            # make sure to include the last interval in the group map
            if (next == length - 1):
                minimum = self.edge_mean(
                    intervals[next][0], self.property_key) - self.epsilon
                maximum = self.edge_mean(
                    intervals[next][-1], self.property_key) + self.epsilon

                for e in intervals[i]:
                    if self.edge_mean(e, self.property_key) <= maximum and e not in intervals[next]:
                        intervals[next].append(e)
                groups[(minimum, maximum)] = intervals[next]

        return groups

    def cluster_groups(self, groups):
        """
            cluster nodes base on their connection with each other

            @param groups
                :type dict
                :description: groups generated by create_intervals method

            :rtype clusters: dict
        """

        clusters = {}
        clusterId = 0
        for e_List in groups.values():
            for i in range(len(e_List)):
                if clusterId not in clusters:
                    clusters[clusterId] = []

                    clusters[clusterId].append(e_List[i].start_node)
                    clusters[clusterId].append(e_List[i].end_node)

                # add nodes with edges in the same cluster
                for edge in e_List:
                    if edge.start_node in clusters[clusterId] and edge.end_node not in clusters[clusterId]:
                        clusters[clusterId].append(edge.end_node)

                    elif edge.end_node in clusters[clusterId] and edge.start_node not in clusters[clusterId]:
                        clusters[clusterId].append(edge.end_node)

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
    
    def get_cluster(self):
        if not self._cluster:
            self.graph()
                        
        return self._cluster
        
    cluster = property(get_cluster)

class NodeMapper(Mapper):
    def __init__(self, edges, data, epsilon=0.5, property_key="reading_level", num_interval=3):
        self.edges = edges
        super().__init__(data, epsilon, property_key, num_interval)

    def cluster_groups(self):
        """
            wrapper function
        """
        groups = self.create_intervals()
        cluster = self.cluster(groups)

        return self.graph_cluster(cluster)

    def create_intervals(self):
        """
            splits the nodes into intervals based on property_key

            @param epsilon
                :type float
                :description: specifies how much to shift the interval to create overlap

            @param edges
                :type list
                :description: list of edges

            @param property_key
                :type string
                :description: the node property used to create interval

            @param num_intervals
                :type int
                :description: number of intervals to create

            :rtype: dict 
        """
        n = len(self.data)
        incr_size = floor(n / self.num_interval)
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
            minimum = intervals[i][0][self.property_key] - self.epsilon
            maximum = intervals[i][-1][self.property_key] + self.epsilon

            # find overlaps
            for j in range(next, len(self.data)):
                if self.data[j][self.property_key] <= maximum and self.data[j] not in intervals[i]:
                    intervals[i].append(self.data[j])

            groups[(minimum, maximum)] = intervals[i]

            # make sure to include the last interval in the group map
            if next == length - 1:
                minimum = intervals[next][0][self.property_key] - self.epsilon
                maximum = intervals[next][-1][self.property_key] + self.epsilon

                for n in intervals[i]:
                    if n[self.property_key] <= maximum and n not in intervals[next]:
                        intervals[next].append(n)
                groups[(minimum, maximum)] = intervals[next]

        return groups

    def cluster(self, groups):
        """
            cluster nodes base on their connection with each other

            @param groups
                :type dict
                :description: groups generated by create_intervals method

            :rtype clusters: dict
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
    def __init__(self, intervals = 0):
        """
            Initializes the TreeMapper object with tree root and filter function
            :param root:
            :param filter_function: Must accept a dictionary object and return a value.
        """
        self._root = None
        self.queue = deque()
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
        :param parent_id:
        :param children:
        :return:
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

    def bfs(self, filter_function = lambda node: sa.convert_score(sa.get_sentiment(node["body"]))):
        """
            Use BFS to visit all nodes in the tree in level order traversal
        :return:
        """
        self.queue.append(self.root)

        while self.queue:
            root = self.queue.popleft()
            if root["children"] is None:
                continue
            # can map level by level by storing children list then mapping the whole level
            # instead of doing children mapping
            self._map(root["id"], root["children"], filter_function)
            for child in root["children"]:
                self.queue.append(child)
             
    def makeTree(self, root, nodes, visited = []):
        for child in nodes:
            if child["parent_id"] == root["id"] or root["composition"] and child["parent_id"] in root["composition"]:                                  
                if "children" in root:
                    root["children"].append(child)
                else:
                    root["children"] = [child]
                    
                if child not in visited:
                    visited.append(child)
                    self.makeTree(child, nodes, visited)
                
        return root
    
    def map(self, children, filter_function):
        """
            Map the children of a node using the filter function.
            Cluster them based on the mapped value
        :param parent_id:
        :param children:
        :return:
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
            node["value"] = value
            node["type"] = "mapper"
            node["id"] = uuid4()
            
            # use the parent id the node with the minimum depth as parent id for the mapper node
            minDepth = float('inf')
            parent_id = None
            
            for child in array:
                node["composition"].append(child["id"])
                if child['depth'] < minDepth:
                    minDepth = child['depth']
                    parent_id = child["parent_id"]

            node["parent_id"] = parent_id

            self._cluster.append(node)
            
    def _createIntervals(self, root, count):        
        # create intervals based on the depth        
        if root["parent_id"]:
            depth = root["depth"]
            self.intervals[depth % count].append(root)
            
        if root["children"]:
            for child in root["children"]:
                self._createIntervals(child, count)

    def _clusterInterval(self, filterFunction):
        for nodes in self.intervals.values():
            self.map(nodes, filterFunction)
    
    def createIntervalsAndCluster(self, root, count = 1, filterFunction = lambda node: sa.convert_score(sa.get_sentiment(node["body"]))):
        # add the depth of the nodes as a property
        self._addDepth(root)
        # create intervals
        self._createIntervals(root, count) 
        # cluster intervals        
        self._clusterInterval(filterFunction)
        
        return self.cluster
        
    def treeHeight(self, root):
        if not root["children"]:
            return 0
        
        height = float('-inf')
        for child in root["children"]:
            height = max(height, self.treeHeight(child) + 1)
        
        return height
      
    def _addDepth(self, root, depth = 0): 
        # add the depth of the node
        root["depth"] = depth
        if root["children"]:
            for child in root["children"]:
                self._addDepth(child, depth + 1)
        
     

