import unittest

from igraph import *

from libs.clustering_algorithms import *
from libs.database_api import *
from libs.graphs import AdjacencyListUnDirected

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
    def test_k_means(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = AdjacencyListUnDirected(*data)
        components = ClusterUtil.label_components(graph.alist)
        clusters = []
        for component in components.values():
            clusters.extend(
                k_means(component, 5, iter_tol=0.00001, prop='reading_level', cluster_tol=50)
            )

        n = len(clusters)
        edges = []

        for i in range(n):
            for j in range(i + 1, n):
                edge = ClusterUtil.connect_clusters(clusters[i], clusters[j], graph)
                if edge:
                    edges.append(edge)
        # print("Cluster count:  ",len(clusters))

    def test_sklearn_kmeans(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = AdjacencyListUnDirected(*data)
        nodes = graph.vertices()
        kmeans = SKLearnKMeans()
        X = kmeans.fit(nodes)

        clusters = defaultdict(Cluster)
        for node in nodes:
            prediction = kmeans.predict(kmeans.transform_node(node))
            clusters[prediction[0]].add_node(node)
        # print("Cluster count:  ",len(clusters))


if __name__ == "__main__":
    unittest.main()
