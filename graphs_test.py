import unittest

import networkx as nx

from libs.database_api import *
from libs.graphs import *

# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


def to_veritces(data):
    vertices = set()

    for e in data:
        vertices.add(e.start_node)
        vertices.add(e.end_node)
    return list(vertices)


class TestClusteringImpl(unittest.TestCase):

    def test_igraph(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = IGraph()
        nodes = set()

        for e in data:
            nodes.add(e.start_node)
            nodes.add(e.end_node)

        graph.add_vertices(nodes)
        graph.add_edges(data)
        json = graph.transform_layout_for_drawing("sugiyama")
        # print(json)

    def test_nx_graph_component(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = NxGraph()
        nodes = set()

        for e in data:
            nodes.add(e.start_node)
            nodes.add(e.end_node)

        graph.add_vertices(nodes)
        graph.add_edges(data)
        json = [
            list(graph.retrieve_edges(subg.edges)) for subg in
            [graph.subgraph(component).copy() for component in nx.connected_components(graph)]
        ]
        print(json)


class TimeGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tested = TimeGraph()
        self.data = query.get_comments_in_article('f3ejzj')
        self.tested.add_edges(self.data)
        self.tested.add_vertices(to_veritces(self.data))

    def test_create_buckets(self):
        self.tested.create_buckets()
        print(self.tested.bucket)


if __name__ == "__main__":
    unittest.main()
