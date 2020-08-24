import unittest

from libs.clustering_algorithms import *
from libs.database_api import *
from libs.graphs import AdjacencyListUnDirected

# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


class TestClusteringImpl(unittest.TestCase):
    def test_mapper_k_means(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = AdjacencyListUnDirected(*data)
        components = ClusterUtil.label_components(graph.list)
        clusters = []
        k_means = MapperKMeans(5, 'reading_level', iter_tol=0.00001, cluster_tol=50)
        for component in components.values():
            clusters.extend(k_means.cluster(component))

        self.assertNotEqual(0, len(clusters))
        print("Cluster:  ", clusters)

    def test_sklearn_kmeans(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = AdjacencyListUnDirected(*data)
        nodes = graph.vertices()
        kmeans = SKLearnKMeans("reading_level")
        clusters = kmeans.cluster(nodes)

        self.assertNotEqual(0, len(clusters))
        print("Clusters:  ", kmeans.cluster(nodes))


if __name__ == "__main__":
    unittest.main()
