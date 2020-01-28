
import sys
sys.path.append("/home/chuk/dev/docker-dev/mapper/discussion_mapper")

from libs.database_api import *
from libs.clustering_algorithms import *
import unittest


# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


class TestClusteringImpl(unittest.TestCase):
    def test_k_means(self):
        data = query.get_comments_in_article('eunf24')
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
            for j in range(i+1, n) :
                edge = ClusterUtil.connect_clusters(clusters[i], clusters[j], graph)
                if edge:
                    edges.append(edge)
        print("Cluster count:  ",len(clusters))

if __name__ == "__main__":
    unittest.main()
