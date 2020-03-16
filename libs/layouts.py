import itertools
from libs.clustering_algorithms import IGraph, NxGraph
import networkx as nx


class LayoutTransformer:
    def __init__(self, clustering_algo):
        self.clustering_algo = clustering_algo

    def layout_d3_fd(self, edges, **params):
        """
            this function is used to create data structure that will be
            serialized to JSON for visualization

            @param edges
                :type list
                :description list of Relationship object
        """
        edges, vertices = self.clustering_algo(edges, **params)
        # dictionary to store index
        output = {}
        # list to store nodes
        nodes = []
        # list to store the link namedtuples
        links = []

        # transforms the edges into a data format D3 will use
        for rel in edges:
            n1 = rel.start_node
            n2 = rel.end_node

            # Coerce py2neo to get all the node properties
            n1['name']
            n2['name']
            if n1['id'] not in output:
                # add node to list
                nodes.append(n1)
                # add node index to index dictionary
                output[n1['id']] = len(nodes) - 1

            if n2['id'] not in output:
                nodes.append(n2)
                output[n2['id']] = len(nodes) - 1

            # create a simple record type for D3 links using the
            # indices in the index dictionary
            links.append({"source": output[n1['id']], "target": output[n2['id']]})

        # create a dictionary containing D3 formatted nodes and links
        output = {"nodes": nodes, "links": links}
        output["nodes"].extend(vertices)

        return output

    def layout_igraph(self, edges, **params):
        layout_algo = params['layout']
        if not self.is_layout_algo_available(layout_algo):
            layout_algo = "sugiyama"

        edges, vertices = self.clustering_algo(edges, **params)
        nodes = []

        for e in edges:
            nodes.append(e.start_node)
            nodes.append(e.end_node)

        nodes.extend(vertices)
        graph = IGraph()
        graph.add_vertices(nodes)

        graph.add_edges(edges)
        return graph.transform_layout_for_drawing(layout_algo)

    def is_layout_algo_available(self, algo):
        return algo.lower() in \
               [
                   "auto", "automatic",
                   "bipartite", "circle",
                   "circular", "dh",
                   "davidson_harel", "drl",
                   "fr", "fruchterman_reigold",
                   "grid", "graphopt",
                   "kk", "kamada_kawai",
                   "lgl", "large", "large_graph",
                   "mds", "random", "rt", "tree"
                                          "rt_circular", "reingold_tilford",
                   "reingold_tilford_circular", "sphere",
                   "star", "sugiyama"
               ]

    def __call__(self, edges, **params):
        if params['layout'] == 'force_directed' or params['layout'] == 'timeline':
            return self.layout_d3_fd(edges, **params)

        return self.layout_igraph(edges, **params)


class LayoutAggregator:
    json = None

    def __init__(self, layout_func):
        self.layout_func = layout_func

    def aggregate(self, edges, **params):
        """
        combines the subgraphs layouts into a single graph layout for display
        :param edges: list of graph edges
        :param params: mapper parameter
        :return: subgraphs layout
        """

        for subgraph_edges in self.connected_components(edges):
            e = list(subgraph_edges)  # consume the generator
            layout = self.layout_func(e, **params)
            self.extend_layout(layout)

        return LayoutAggregator.json

    def extend_layout(self, layout):
        if LayoutAggregator.json is None:
            LayoutAggregator.json = layout

        else:
            if "coords" in LayoutAggregator.json:
                LayoutAggregator.json["coords"].extend(layout["coords"])

            LayoutAggregator.json["links"].extend(layout["links"])
            LayoutAggregator.json["nodes"].extend(layout["nodes"])

    def connected_components(self, edges):
        """
        creates a subgraph for all the connected components in the graph
        :param edges: graph edges
        :return: subgraph generator
        """
        graph = NxGraph()
        graph.add_vertices(set(itertools.chain.from_iterable([e.start_node, e.end_node] for e in edges)))
        graph.add_edges(edges)

        for component in nx.connected_components(graph):
            subgraph = graph.subgraph(component).copy()
            yield graph.retrieve_edges(subgraph.edges)

    def __call__(self, edges, **params):
        LayoutAggregator.json = None
        return self.aggregate(edges, **params)
