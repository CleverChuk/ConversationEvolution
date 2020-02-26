
from libs.database_api import *
from libs.clustering_algorithms import *
from igraph import *
import unittest


# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


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
            for j in range(i+1, n) :
                edge = ClusterUtil.connect_clusters(clusters[i], clusters[j], graph)
                if edge:
                    edges.append(edge)
        print("Cluster count:  ",len(clusters))
    
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
        print("Cluster count:  ",len(clusters))

    def test_igraph(self):
        data = query.get_comments_in_article('f3ejzj')
        graph = IGraph()
        nodes = []
        
        for e in data:
            nodes.append(e.start_node)
            nodes.append(e.end_node)
        
        graph.add_vertices(nodes)
        graph.add_edges(data)
        json = graph.transform_layout_for_drawing("sugiyama")
        print(json)

if __name__ == "__main__":
    unittest.main()
