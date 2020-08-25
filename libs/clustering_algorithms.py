import random
from collections import defaultdict
from math import sqrt, ceil

from sklearn.cluster import KMeans
from sklearn.feature_extraction import DictVectorizer

from libs.utils import ClusterUtil

random.seed(0)


class BaseAlgorithm:
    def cluster(self, nodes):
        raise NotImplemented


class SKLearnKMeans(BaseAlgorithm, KMeans):
    def __init__(self, lens, **kwargs):
        super().__init__(**kwargs)
        self.lens = lens
        self.vect = DictVectorizer()

    def fit(self, X, y=None, sample_weight=None):
        x = (self.extract_lens(node) for node in X)
        _X = self.vect.fit_transform(x)
        return super().fit(_X, y, sample_weight)

    def transform_node(self, node):
        return self.vect.transform(self.extract_lens(node))

    def extract_lens(self, node):
        return {self.lens: node.get(self.lens, 0)}

    def cluster(self, nodes):
        self.fit(nodes)
        clusters = defaultdict(Cluster)
        for node in nodes:
            prediction = self.predict(self.transform_node(node))
            clusters[prediction[0]].add_node(node)

        return [c.to_node() for c in clusters.values()]


class Cluster:
    # could use a list for prop to make it general
    def __init__(self, prop="reading_level", node=None, tol=0.01):
        self.mean = 0 if node is None else node[prop]
        self.node = None  # store node representation of the cluster
        self.has_linked = False
        self.count = 1
        self.nodes = [] if node is None else [node]
        self.tol = tol
        self.prop = prop
        self.component_id = random.randint(
            0, 400000000) if node is None else node['component_id']

    def add_to(self, node):
        if not node['grouped']:
            self.count += 1
            node['grouped'] = True
            self.nodes.append(node)
            self._update_mean()

    def add_node(self, node):
        self.nodes.append(node)

    def _update_mean(self):
        total = 0
        for node in self.nodes:
            total += node[self.prop]

        self.mean = round(total / self.count,
                          ClusterUtil.count_decimal_places(self.tol))

    def reset(self):  # reset the cluster for repeat computation
        if len(self.nodes):
            keep = self.nodes.pop(0)
            tol = self._distance_metric(keep)

            for node in self.nodes:
                temp = self._distance_metric(node)
                if temp < tol:  # keep node nearest to mean
                    keep['grouped'] = False
                    keep = node
                    tol = temp
                else:
                    node['grouped'] = False

            # reset properties
            self.nodes.clear()
            self.nodes.append(keep)
            self.count = 1

    def is_empty(self):
        return len(self.nodes) == 0

    def _distance_metric(self, node):
        # calculate the Euclidean distance
        if self.is_empty():
            return node[self.prop]  # return value for node if cluster is empty
        return sqrt(pow(self.mean - node[self.prop], 2))

    def is_reachable(self, node):  # check if node is in the same components
        if self.is_empty():
            return True
        return self.component_id == node["component_id"]

    def __median(self):
        vals = [node[self.prop] for node in self.nodes]
        vals.sort()
        if self.count % 2 == 0:
            return (vals[self.count // 2] + vals[self.count // 2 + 1]) / 2

        return vals[self.count // 2]

    def dist_from(self, node):
        return self._distance_metric(node)

    def is_related(self, cluster, graph):
        for n1 in cluster.nodes:
            for n2 in self.nodes:
                if graph.is_connected(n1, n2):
                    return True
        return False

    def to_node(self, aggregate_by='mean'):
        if self.count and self.node is None:
            self.node = ClusterUtil.create_cluster_node('mapper', aggregate_by, self.nodes,
                                                        ClusterUtil.attr_list(self.nodes[0]))

        return self.node

    def __eq__(self, c):
        if isinstance(c, Cluster):
            return self.component_id == c.component_id
        return False

    def __repr__(self):
        return f"N = {self.count}, has_linked: {self.has_linked}, component id: {self.component_id}"


class MapperKMeans(BaseAlgorithm):
    def __init__(self, n, lens, iter_tol=0.001, cluster_tol=0.001, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.lens = lens
        self.iter_tol = iter_tol
        self.cluster_tol = cluster_tol

    def score(self, clusters, tol):
        total = 0
        n = len(clusters)
        for c in clusters:
            total += c.mean

        return round(total / n, ClusterUtil.count_decimal_places(tol))

    def reset_clusters(self, clusters):
        for c in clusters:
            c.reset()

    def cluster(self, nodes):
        # sensitive to first node picked
        N = len(nodes)
        if self.n > N:
            self.n = ceil(N / 2)

        init_nodes = random.choices(nodes, k=self.n)
        for node in init_nodes:
            node['grouped'] = True

        clusters = [Cluster(self.lens, init_nodes[i], tol=self.cluster_tol)
                    for i in range(self.n)]
        diff = 0
        while True:
            for node in nodes:
                closest_cluster = None
                dist_score = float('inf')
                for cluster in clusters:
                    temp = cluster.dist_from(node)
                    if temp < dist_score:
                        closest_cluster = cluster
                        dist_score = temp

                if closest_cluster.is_reachable(node):
                    closest_cluster.add_to(node)

            if abs(self.score(clusters, self.iter_tol) - diff) <= self.iter_tol:
                break
            else:
                diff = self.score(clusters, self.iter_tol)
                self.reset_clusters(clusters)

        return [c.to_node() for c in clusters]
