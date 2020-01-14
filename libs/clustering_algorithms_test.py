
import sys
sys.path.append("/home/chuk/dev/docker-dev/mapper/discussion_mapper")

from database_api import *
from clustering_algorithms import *
import unittest


# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


class TestClusteringImpl(unittest.TestCase):
    def test_k_means(self):
        data = query.get_comments_in_article('enzgz6')
        graph = AdjacencyListUnDirected(*data)
        clusters = k_means(graph.vertices(), 5, iter_tol=0.00001, prop='reading_level', cluster_tol=0.1)
        print("Cluster count:  ",len(clusters))

if __name__ == "__main__":
    unittest.main()
