from collections import defaultdict

DEFAULT_MEAN = 0.0

class AdjacencyMAtrixUnDirected:
    def __init__(self, *edges): # list of edge object with start_node and end_node properties
        self._list = defaultdict(list)
        self.build(edges)

    def build(self, edges):
        for edge in edges:
            self._list[edge.start_node].append(edge.end_node)
            self._list[edge.end_node].append(edge.start_node)
    
    def is_connected(self, n1, n2):
        return n2 in self._list[n1] or n1 in self._list[n2]

    def neighbors(self, n0):
        return self._list[n0]

    def vertices(self):
        v = set()
        for nodes in self._list.values():
            v.update(nodes)        
        return v



class Cluster:
    def __init__(self, prop, tol = 0.01): # could use a list for prop to make it general
        self.mean = DEFAULT_MEAN
        self.value = 0
        self.count = 0
        self.nodes = []
        self.tol = tol
        self.prop = prop

    def __count_round(self):
        temp = str(self.tol)
        return len(temp) - temp.find('.')

    def add_to(self, node):
        if not node['grouped']:
            self.count += 1
            node['grouped'] = True
            self.nodes.append(node)
            self._update_mean()

    def _update_mean(self):
        total = 0
        for node in self.nodes:
            total += node[self.prop]

        self.mean = round(total/self.count, self.__count_round())

    def re_init(self): # reinitialize the cluster for repeat computation
        if len(self.nodes):
            keep = self.nodes.pop(0) # keep node nearest to mean
            tol = self._dist_mean(keep)

            for node in self.nodes:
                temp = self._dist_mean(node)
                if temp < tol:            
                    keep['grouped'] = False     
                    keep = node
                    tol = temp
                else:
                    node['grouped'] = False

            # initialize properties
            self.nodes.clear()
            self.nodes.append(keep)
            self.count = 1

    def _dist_mean(self, node): # could use euclidean distance for multivariable prop
        # calculate the linear distance from mean
        if self.mean == DEFAULT_MEAN:
            return node[self.prop]
        return abs(self.mean - node[self.prop])
    
    def is_near(self, node): # check if nide is within cluster distance tolerance
        if self.mean != DEFAULT_MEAN:
            return self._dist_mean(node) <= self.tol

        return True

    def dist_from(self, node):
        return self._dist_mean(node)

    def is_related(self, cluster, graph): # connect related clusters
        for n1 in cluster.nodes:
            for n2 in self.nodes:
                if graph.is_connected(n1, n2):
                    return True
        return False

# functions
def score(clusters):
    total = 0
    n = len(clusters)
    for c in clusters:
        total += c.mean

    return round(total / n, 2)

def re_init_clusters(clusters):
    for c in clusters:
        c.re_init()

def k_means(nodes, k, prop='sentiment_score', iter_tol=0.001, cluster_tol=0.001):
    # sensitive to first node picked
    clusters = [Cluster(prop, tol=cluster_tol) for i in range(k)]
    diff = 0
    while True:
        
        for node in nodes:
            clique = None
            dist_score = float('inf')
            for cluster in clusters:
                temp = cluster.dist_from(node)
                if temp < dist_score:
                    clique = cluster
                    dist_score = temp
            
            clique.add_to(node)
        
        if abs(score(clusters) - diff) <= iter_tol:
            break
        else:
            diff  = score(clusters)
            re_init_clusters(clusters)

    return clusters