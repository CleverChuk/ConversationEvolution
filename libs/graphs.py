import datetime as dt
import random
from collections import defaultdict
from typing import List

import igraph
import networkx as nx
from py2neo import Relationship

from libs.models import Node, Edge

random.seed(0)


class AdjacencyListUnDirected:
    def __init__(self, *edges):  # list of edge object with start_node and end_node properties
        self._list = defaultdict(list)
        self.build(edges)

    @property
    def list(self):
        return self._list

    def build(self, edges):
        for edge in edges:
            s = edge.start_node
            d = edge.end_node
            # TODO use id instead of whole object
            if s['id'] != d['id']:  # eliminate self loops and force property download from neo4j
                self.list[s].append(d)
                self.list[d].append(s)

    def is_connected(self, n1, n2):
        return n2 in self.list[n1] or n1 in self.list[n2]

    def neighbors(self, n0):
        return self.list[n0]

    def vertices(self):
        return list(self.list.keys())


class IGraph(igraph.Graph):
    translate_vector = [0, 0, 0]

    def __init__(self):
        self.mapping = {}
        super().__init__()

    def _create_mapping(self, nodes):
        temp_set = set(nodes)
        for i, node in enumerate(temp_set):
            self.mapping[node] = i

    def add_vertices(self, nodes):
        self._create_mapping(nodes)
        super().add_vertices(len(self.mapping))

    def transform(self, edges_list, mapping):
        temp = []
        for edge in edges_list:
            start_node, end_node = edge.start_node, edge.end_node
            temp.append((mapping[start_node], mapping[end_node]))

        return temp

    def add_edges(self, edge_list):
        if not len(self.mapping):
            raise RuntimeError("must add vertices first")

        if not isinstance(edge_list, list):
            raise RuntimeError(f"Expected a list, but got -> {str(edge_list)}")

        if not len(edge_list):  # ignore empty list
            return

        if not isinstance(edge_list[0], Relationship) and not isinstance(edge_list[0], Edge):
            raise RuntimeError(
                f"Expected a list of {str(Relationship)}, but got a list of {str(edge_list[0])}")

        super().add_edges(self.transform(edge_list, self.mapping))

    def transform_layout_for_drawing(self, layout_algo):
        layout = self.layout(layout=layout_algo)
        layout.scale(100)

        json = {"coords": layout.coords}
        nodes = [None] * len(self.mapping)

        for node, i in self.mapping.items():
            node['x'] = layout.coords[i][0]
            node['y'] = layout.coords[i][1]
            nodes[i] = node

        json["nodes"] = nodes

        links = []
        for edge in self.es:
            links.append(
                {
                    "source": nodes[edge.source],
                    "target": nodes[edge.target]
                }
            )
        json["links"] = links

        return json

    @classmethod
    def update_translate_vector(cls):
        if cls.translate_vector[2] == 0:
            cls.translate_vector[2] += 1
            return

        print("Translation vector", cls.translate_vector)

        cls.translate_vector[0] += 100
        cls.translate_vector[1] += 100
        cls.translate_vector[2] += 1


class NxGraph(nx.Graph):
    def __init__(self, data=None, **kwargs):
        self.forward_mapping = {}
        self.backward_mapping = {}
        super().__init__(incoming_graph_data=data, **kwargs)

    def add_vertices(self, nodes, forward_mapping=None, backward_mapping=None):
        if forward_mapping is None or backward_mapping is None:
            for i, node in enumerate(nodes):
                self.forward_mapping[node] = i
                self.backward_mapping[i] = node
        else:
            self.forward_mapping = forward_mapping
            self.backward_mapping = backward_mapping

        return self.forward_mapping, self.backward_mapping

    def add_edges(self, edges):
        if not len(self.forward_mapping):
            raise Exception("Must call 'add_nodes' first")

        _edges = (
            (self.forward_mapping[e.start_node], self.forward_mapping[e.end_node])
            for e in edges
        )

        self.add_edges_from(_edges)

        return _edges

    def retrieve_nodes(self, ids):
        for i in ids:
            yield self.backward_mapping[i]

    def retrieve_edges(self, edges):
        """
        maps integer based edge to object based edge
        :param edges: list of integer edges
        :return: generator of object based edges
        """
        for i, j in edges:
            yield Edge(self.backward_mapping[i], self.backward_mapping[j])


class TimeGraph(AdjacencyListUnDirected):
    Y_OFFSET = 100

    def __init__(self, time_width_hours: int = 1, *edges):
        super().__init__(*edges)
        self.bucket = defaultdict(list)
        self.time_width = time_width_hours
        self.edges = None
        self.vertz = None
        self.forward_mapping = {}
        self.bucket_layout = None

    def add_edges(self, edges: List[Edge]):
        super(TimeGraph, self).build(edges)
        self.vertz = self.vertices()
        self.vertz.sort(key=lambda v: v['timestamp'])
        self._map()

    def add_vertices(self, nodes: List[Node]):
        pass

    def _map(self):
        for i, v in enumerate(self.vertz):
            self.forward_mapping[v] = i

    def create_buckets(self):
        time_delta = dt.timedelta(hours=self.time_width)
        min_time = min(self.vertz, key=lambda x: x['timestamp'])['timestamp']
        min_time = dt.datetime.fromtimestamp(min_time)

        temp = min_time
        for v in self.vertz:
            timestamp = dt.datetime.fromtimestamp(v['timestamp'])
            if temp <= timestamp < temp + time_delta:
                self.bucket[(temp, temp + time_delta)].append(v)

            else:
                temp += time_delta
                self.bucket[(temp, temp + time_delta)].append(v)

    def bucket_mapping(self, bucket):
        mapping = {}
        if len(self.forward_mapping):
            for v in bucket:
                mapping[v] = self.forward_mapping[v]
        return mapping

    def extend_mapping(self, mapping):
        if not isinstance(mapping, dict):
            raise Exception("Mapping must be type of dict")

        self.forward_mapping.update(mapping)

    def set_bucket_layout(self, layout):
        self.bucket_layout = layout

    def link_nodes(self):
        links = []
        nodes = []
        coords = []
        x_avg, y_avg = None, None
        for idx, layout in self.bucket_layout.items():
            if x_avg is None:
                x_avg = sum([n['x'] for n in layout['nodes']]) / len(layout['nodes'])
                y_avg = sum([n['y'] for n in layout['nodes']]) / len(layout['nodes'])
            nodes.extend(layout["nodes"])

        length = len(nodes)
        for i in range(length):
            for j in range(i + 1, length):
                if self.is_connected(nodes[i], nodes[j]):
                    links.append(
                        {
                            "source": nodes[i],
                            "target": nodes[j]
                        }
                    )
        t = None
        incr = 0
        for idx, layout in self.bucket_layout.items():
            if t is None or idx[0] > t:
                t = idx[0]
                incr += x_avg

            vertices = layout['nodes']
            for node in vertices:
                node['time'] = min(idx)  # set time coordinate
                node['x'] = incr
                node['y'] += (y_avg * TimeGraph.Y_OFFSET)

        return {"nodes": nodes, "links": links, "coords": coords}

    @property
    def buckets(self):
        if not len(self.bucket):
            self.create_buckets()
        return self.bucket.items()
