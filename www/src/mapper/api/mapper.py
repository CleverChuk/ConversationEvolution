# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to map the main to a subgraph that approximates the main graph.
#          It is important to know that the mapper functions
#          assumes that the nodes given to it are of the same Type.

from collections import defaultdict, OrderedDict
from .models import Node
import random
from math import ceil, floor
import statistics as stats

NEW_ID = 0
ALPHA = 97
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

    @classmethod
    def cast(cls, py2neo_rel):
        return cls(py2neo_rel.start_node, py2neo_rel.end_node)

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
        return self.start_node['type'] + "->"+self.end_node['type']


class Mapper:
    JACCARD_THRESH = 0.1

    def __init__(self, data=[], epsilon=0.5, property_key="reading_level", num_interval=3):
        self.data = data
        self.epsilon = epsilon
        self.property_key = property_key
        self.num_interval = num_interval
        # For nodes without property_key as field
        self.filtered_in_data = []
        self._average = False # use to determine how to aggregate cluster nodes- mean or median

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
            new_nodes[name] = self.cluster_nodes(name, cluster, self.attr_list(cluster[0]))
            new_nodes[name]['radius'] += len(cluster)*5

        # connect clusters base on node overlap
        names = list(clusters.keys())
        clusters = list(clusters.values())
        n = len(names)

        for i in range(n):
            cluster = set(clusters[i])
            for j in range(i+1, n):
                nextCluster = set(clusters[j])
                # skip this edge if the Jaccard index is less than 0.1
                j_index = round(self.jeccard_index(cluster, nextCluster), 2)
                if j_index < Mapper.JACCARD_THRESH:
                    continue

                if not cluster.isdisjoint(nextCluster) and new_nodes[names[i]] != new_nodes[names[j]]:
                    edges.append(Edge(new_nodes[names[i]], new_nodes[names[j]],
                                      id=id, type=j_index)
                                 )
                    id += 1

        # assumes filtered is always of type author and sentiment
        authors = []
        sentiments = []
        # #TODO: add if statement to ignore or perform this task
        for link in self.filtered_in_data:
            if link[0]['type'] == 'author':
                authors.append(link[0])

        #     elif link[0]['type'] == 'sentiment':
        #         sentiments.append(link[0])

            if link[1]['type'] == 'author':
                authors.append(link[1])
        #     elif link[1]['type'] == 'sentiment':
        #         sentiments.append(link[1])

        N = len(edges)
        # #TODO: add if statement to ignore or perform this task

        for i in range(N):
            for node in authors:
                # check if the author's comment contributed to this cluster
                if edges[i][0]['authors']:
                    a = edges[i][0]['authors'].get(node['name'])
                    if a != None:
                        edges.append(Edge(node, edges[i][0]))
                        # Remove author to avoid creating multiple author edges to all contributing nodes
                        del edges[i][0]['authors'][a]

                if edges[i][1]['authors']:
                    a = edges[i][1]['authors'].get(node['name'])
                    if a != None:
                        edges.append(Edge(node, edges[i][1]))
                        # Remove author to avoid creating multiple author edges to all contributing nodes
                        del edges[i][1]['authors'][a]

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

    def cluster_nodes(self, name, cluster, property_keys):
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
        global NEW_ID, ALPHA
        if not isinstance(cluster, list) and not isinstance(property_keys, list):
            raise Exception("cluster and property_keys must be lists")

        numerical_variables = []
        cluster_node = Node({'subreddit': cluster[0]['subreddit'], 'name': name})
        category_variable = defaultdict(int)

        mode_value = 0
        mode_var = None
        for property_key in property_keys:
            for node in cluster:
                tp = node[property_key]
                if isinstance(tp, str):  # use mode for categorical variables
                    category_variable[tp] += 1
                    if category_variable[tp] > mode_value:
                        mode_value = category_variable[tp]
                        mode_var = tp
                else:
                    numerical_variables.append(tp)

                # add authors dictionary to cluster use to form edge
                if cluster_node['authors']:
                    cluster_node['authors'][node['author']] = node['author']

                else:
                    cluster_node['authors'] = {node['author']: node['author']}

            if len(numerical_variables) != 0:  # use median for numerical variables
                if self._average:
                    cluster_node[property_key] = float(round(stats.mean(numerical_variables), 4))
                    numerical_variables.clear()
                else:
                    numerical_variables = sorted(numerical_variables)
                    cluster_node[property_key] = float(round(stats.median(numerical_variables), 4))
                    numerical_variables.clear()

            else:
                cluster_node[property_key] = str(mode_var)
                mode_value = 0
                category_variable.clear()

        d = {}
        tt = "type"
        dd = "id_0"
        cluster_node.id = str(NEW_ID) + chr(ALPHA)

        d["id"] = str(NEW_ID) + chr(ALPHA)
        t = cluster_node.pop(tt, "")
        id_0 = cluster_node.pop(dd, "")

        d.update(cluster_node)
        d[tt] = t
        d[dd] = id_0

        # updates the underlying node dictionary so it is easy to
        # write to csv
        cluster_node = d

        # unique ids for the nodes
        NEW_ID += 1
        ALPHA += 1
        if (ALPHA > 122):
            ALPHA = 97

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

        p1 = edge[0][property_key]
        p2 = edge[1][property_key]
        if isinstance(p1, str) or isinstance(p2, str):
            raise TypeError("property_key value must be numeric")

        return round((p1+p2)/2, 2)


class EdgeMapper(Mapper):
    def __init__(self, edges, epsilon=0.5, property_key="reading_level", num_interval=3):        
        
        def filter_out(edge):
            return  edge.start_node['type'] == 'comment' and edge.end_node['type'] == 'comment'

        def filter_in(edge):
            return  edge.start_node['type'] != 'comment' or edge.end_node['type'] != 'comment'


        self.filtered_data = list(filter(filter_out, edges))
        self.filtered_data = sorted(self.filtered_data, key = lambda link : self.edge_mean(link, property_key))
        
        super().__init__(self.filtered_data, epsilon, property_key, num_interval)
        self.filtered_in_data = list(filter(filter_in, edges))

    def cluster(self):
        """
            wrapper function
        """
        groups = self.create_intervals()
        cluster = self.cluster_groups(groups)

        return self.graph_cluster(cluster)

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
        incr_size = floor(n/self.num_interval)

        if incr_size == 0:
            incr_size = 1

        # create the intervals using property value to mark the range bounds
        for i in range(0, n, incr_size):
            intervals.append(self.data[i:i+incr_size])

        groups = defaultdict(list)  # map to hold groups
        length = len(intervals)
        for i in range(length-1):
            next = i+1

            # adjust the overlap range by epsilon
            minimum = self.edge_mean(intervals[i][0], self.property_key) - self.epsilon
            maximum = self.edge_mean(intervals[i][-1], self.property_key) + self.epsilon
            
            # create the overlap between interval i and i+1
            for e in intervals[next]:
                if self.edge_mean(e, self.property_key) <= maximum and e not in intervals[i]:
                    intervals[i].append(e)

            groups[(minimum, maximum)] = intervals[i]

            # make sure to include the last interval in the group map
            if(next == length-1):
                minimum = self.edge_mean(intervals[next][0], self.property_key) - self.epsilon
                maximum = self.edge_mean(intervals[next][-1], self.property_key) + self.epsilon
                
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

                    clusters[clusterId].append(e_List[i][0])
                    clusters[clusterId].append(e_List[i][1])

                # add nodes with edges in the same cluster
                for edge in e_List:
                    if edge[0] in clusters[clusterId] and edge[1] not in clusters[clusterId]:
                        clusters[clusterId].append(edge[1])

                    elif edge[1] in clusters[clusterId] and edge[0] not in clusters[clusterId]:
                        clusters[clusterId].append(edge[0])

                clusterId += 1

        temp = list(clusters.keys())
        indices = []
        # find the index duplicate clusters
        for i in temp:
            s1 = set(clusters[i])
            for j in temp[i+1:]:
                s2 = set(clusters[j])
                if s2 == s1:
                    indices.append(j)

        # remove duplicate clusters
        for i in indices:
            clusters.pop(i, "d")

        return clusters

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
        incr_size = floor(n/self.num_interval)
        if incr_size == 0:
            incr_size = 1

        intervals = []
        # create the intervals using property_key value to mark the range bounds
        for i in range(0, n, incr_size):
            n = self.data[i:i+incr_size]
            intervals.append(n)

        groups = defaultdict(list)  # map to hold groups
        length = len(intervals)

        for i in range(length-1):
            next = i + 1
            minimum = intervals[i][0][self.property_key] - self.epsilon
            maximum = intervals[i][-1][self.property_key] + self.epsilon

            # find overlaps
            for j in range(next, len(self.data)):
                if self.data[j][self.property_key] <= maximum and self.data[j] not in intervals[i]:
                    intervals[i].append(self.data[j])

            groups[(minimum, maximum)] = intervals[i]

            # make sure to include the last interval in the group map
            if(next == length-1):
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
            for j in temp[i+1:]:
                s2 = set(clusters[j])
                if s2 == s1:
                    indices.append(j)

        # remove duplicate clusters
        for i in indices:
            clusters.pop(i, "d")
        return clusters
