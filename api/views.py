from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from libs import database_api
from libs.models import TreeNode
from libs.mapper import EdgeMapper, Edge, TreeMapper
import json
import threading
import numpy as np
import os
from libs.clustering_algorithms import k_means, AdjacencyListUnDirected as AList, ClusterUtil

# neo4j configs
NEO4J_URL = os.environ["NEO4J_URL"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]


print("="*100)
print(f"{NEO4J_URL}, {NEO4J_USERNAME}, {NEO4J_PASSWORD}")
print("="*100)
# constants
ARTICLE_ID = 'article_id'
# Create db layer object and pass it to the query object
db_layer = database_api.Neo4jLayer()
query = database_api.Query(db_layer)


# Create your views here.


def all_nodes(request):
    """
        return the whole graph from database
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    elif request.method == "GET":
        data = query.all()
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def get_nodes(request):
    """
        return all the nodes in the database
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    if request.method == "GET":
        return JsonResponse({'nodes': query.nodes()})
    else:
        return HttpResponse(status=406)


def get_nodes_by_label(request, **param):
    """
        return nodes with given label
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    label = param.get("label", None)
    if request.method == "GET" and label:
        data = query.get_nodes_by_label(label)
        return JsonResponse({"nodes": data})
    else:
        return HttpResponse(status=406)


def get_relationship_by_type(request, **param):
    """
        return relationship/edges with the given type
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    _type = param.get("type", None)
    if request.method == "GET" and _type:
        data = query.get_relationship_by_type(_type)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def equal_str(request, **param):
    """
        return all nodes where the field value equals the given string value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:
        data = query.get_equal_str(field, value)
        data = database_api.D3helper.graph_transform(*data)

        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def equal(request, **param):
    """
        return all nodes where the field value equals the given value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":  # handle prefetch request
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def greater(request, **param):
    """
        return all nodes where the field value is great than the given numeric value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_greater(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def greater_or_equal(request, **param):
    """
        return all nodes where the field value is greater than or equal to the given numeric value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_greater_or_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def less(request, **param):
    """
        return all nodes where the field value is less than the given numeric value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:
        data = query.get_less(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def less_or_equal(request, **param):
    """
        return all nodes where the field value is less than or equal to the given numeric value
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_less_or_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


@csrf_exempt  # hack find a better way
def get_edges_in_article(request):
    """
        return all edges/relationship in the given article and transform them based on the request params
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Methods"] = "POST"
        response["Access-Control-Allow-Origin"] = "*"

        return response

    if request.method == "POST":
        # TODO Handle empty body and missing param error
        body = json.loads(request.body)
        ids = body["ids"]
        is_mapper = body["mapper"]

        if ids:
            data = {}
            threads = []

            for id in ids:  # load graph for each of the article with `id`
                t = threading.Thread(target=load_edges_task, args=(id, data))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            if body['layout'] == 'hierarchy':  # transform data for hierarchical layout
                _tree = TreeNode("root", type="root")
                if is_mapper:  # run mapper if true
                    for i in range(len(data)):
                        # run mapper on each article graph
                        _tree.add_child(_mapper_hierarchy(
                            data[ids[i]], ids[i], "article", **body["m_params"]))
                else:
                    for i in range(len(data)):
                        _tree.add_child(_hierarchy(
                            data[ids[i]], ids[i], "article"))

                response = JsonResponse(_tree)
                response["Content-type"] = 'application/json'
                response["Access-Control-Allow-Origin"] = "*"
                return response

            # transform data for force directed layout
            elif body['layout'] == 'force_directed':
                if len(data) > 1:
                    data = list(data.values())
                    temp = data[0]
                    for i in range(1, len(data)):  # flatten the matrix
                        temp.extend(data[i])

                    data = temp
                else:
                    data = list(data.values())[0]

                if is_mapper:
                    temp = _mapper_force_directed(data, **body["m_params"])

                else:
                    temp = database_api.D3helper.graph_transform(*data)

                response = JsonResponse(temp)
                response["Content-type"] = 'application/json'
                response["Access-Control-Allow-Origin"] = "*"
                return response
            else:
                response = JsonResponse({"unknown layout": body['layout']})
                response["Content-type"] = 'application/json'
                response["Access-Control-Allow-Origin"] = "*"
                return response
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=406)


def get_all_article(request):
    """
        return all article nodes in the database
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    if request.method == "GET":
        data = query.get_all_articles()
        return JsonResponse({"data": data})

    return HttpResponse(status=406)


def get_articles_in_subreddit(request, **params):
    """
        return all article nodes that belong to the given subreddit
        @params:
            - request: request object(see Django doc)
            - params: captured parameters from the request (see urls.py)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    elif request.method == "GET":
        subreddit = params.get("subreddit", None)
        if subreddit:
            data = query.get_articles_in_subreddit(subreddit)
            # data = dict(enumerate(data))
            response = JsonResponse(data, safe=False)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET"

            return response

        else:
            response = HttpResponse(status=400)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET"
            return response

    else:
        response = HttpResponse(status=406)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response


def get_edges_in_subreddit(request):
    """
        return all edges/relationship in the given subreddit
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    elif request.method == "GET":
        subreddit = request.GET.get("subreddit", None)
        layout = request.GET.get("layout", "force_directed")
        # TODO add hierarchy return statement here
        print("get_edges_in_subreddit", request.GET)
        if subreddit:
            data = query.get_edges_in_subreddit(subreddit)
            if layout == 'force_directed':
                data = database_api.D3helper.graph_transform(*data)
            else:
                nodes = edges_to_nodes(data)
                tree_mapper = TreeMapper()
                # make tree from edges
                data = tree_mapper.make_tree(
                    TreeNode(subreddit, type="subreddit"), nodes)

            response = JsonResponse(data)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET"

            return response
        else:
            response = HttpResponse(status=400)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET"
            return response
    else:
        response = HttpResponse(status=406)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response


def get_topological_lens(request):
    """
        return all the available topological lenses
        @params:
            - request: request object(see Django doc)
    """
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response

    response = JsonResponse({"data": db_layer.get_topological_lens()})
    response["Access-Control-Allow-Origin"] = "*"
    return response


def _mapper_force_directed(data, **params):
    """
        transform data to a force directed mapper graph
        @params:
            - data: nodes
            - params: mapper parameters
    """
    # extract the query passed in the url
    lens = 'reading_level' if 'lens' not in params else params['lens']
    interval = 3 if 'interval' not in params else int(params['interval'])
    epsilon = 0.5 if 'epsilon' not in params else float(params['epsilon'])

    mode = 'median' if 'mode' not in params else params['mode']
    algorithm = 'cc' if 'clustering_algorithm' not in params else params[
        'clustering_algorithm']  # no implementation for this yet

    print("Creating force directed graph")
    if algorithm == 'cc':
        mapper = EdgeMapper(data, property_key=lens,
                            epsilon=epsilon, num_interval=interval)
        mapper.average = True if mode == 'mean' else False
        data = mapper.cluster

    elif algorithm == 'k-means' or algorithm == "kmeans":
        data, nodes = _cluster_with_kmeans(data, **params)
        data = database_api.D3helper.graph_transform(*data)
        data['nodes'].extend(nodes)

        return data

    return database_api.D3helper.graph_transform(*data)


def _mapper_hierarchy(data, root_id, root_type, **params):
    """
        transform data to a hierarchy mapper graph
        @params:
            - data: nodes
            - root_id: id of root node
            - root_type: type of root node
            - params: mapper parameters
    """
    # extract the query passed in the url
    lens = 'reading_level' if 'lens' not in params else params['lens']
    interval = 3 if 'interval' not in params else int(params['interval'])
    epsilon = 0.5 if 'epsilon' not in params else float(params['epsilon'])

    mode = 'median' if 'mode' not in params else params['mode']
    algorithm = 'cc' if 'clustering_algorithm' not in params else params[
        'clustering_algorithm']  # no implementation for this yet

    print("Creating hierarchy")
    nodes = edges_to_nodes(data)
    tree_mapper = TreeMapper()

    def filter_function(node):
        if lens in node:
            return node[lens]
        return 0

    # make tree from edges
    hierarchy = tree_mapper.make_tree(TreeNode(root_id, type=root_type), nodes)

    # map the edges using default filter function
    cluster = tree_mapper.execute(
        hierarchy, interval, filter_function=filter_function)

    # make tree from mapper nodes
    return tree_mapper.make_tree(TreeNode(root_id, type=root_type), cluster)


def _hierarchy(data, root_id, root_type):
    """
        create a hierarchy from data root at node with root_id
        @params:
            - data: nodes
            - root_id: id of root node
            - root_type: type of root node
    """
    print("Creating hierarchy")
    nodes = edges_to_nodes(data)
    tree_mapper = TreeMapper()

    root = TreeNode(root_id, type=root_type)
    root["comment_count"] = len(nodes)
    # make tree from edges
    return tree_mapper.make_tree(root, nodes)


def _cluster_with_kmeans(edges, **params):
    print("Processing with K-means")
    lens = 'reading_level' if 'lens' not in params else params['lens']
    k = 10 if 'k' not in params else int(params['k'])
    epsilon = 0.5 if 'epsilon' not in params else float(params['epsilon'])
    mode = 'mean' if 'mode' not in params else params['mode']

    graph = AList(*edges)
    components = ClusterUtil.label_components(graph.alist)
    clusters = []
    for component in components.values():
        clusters.extend(
            k_means(component, k, iter_tol=0.00001, prop=lens, cluster_tol=epsilon)
        )
    
    n = len(clusters)
    edges = []

    for i in range(n):        
        for j in range(i+1, n) :
            edge = ClusterUtil.connect_clusters(clusters[i], clusters[j], graph)
            if edge:
                edges.append(edge)

    nodes = [c.to_node() for c in clusters if not c.has_linked]
    return edges, filter(lambda n: n is not None, nodes)


@DeprecationWarning
def mapper_graph(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response

    elif request.method == "GET":
        # extract the query passed in the url
        lens = 'reading_level' if 'lens' not in request.GET else request.GET['lens']
        interval = 3 if 'interval' not in request.GET else int(
            request.GET['interval'])
        epsilon = 0.5 if 'epsilon' not in request.GET else float(
            request.GET['epsilon'])

        mode = 'median' if 'mode' not in request.GET else request.GET['mode']
        layout = 'hierarchy' if 'graph_layout' not in request.GET else request.GET[
            'graph_layout']
        algorithm = 'cc' if 'clustering_algorithm' not in request.GET else request.GET[
            'clustering_algorithm']  # no implementation for this yet
        subreddit = 'legaladvice' if 'subreddit' not in request.GET else request.GET[
            'subreddit']
        data = db_layer.get_edges_in_subreddit(subreddit)

        print("Params", request.GET)
        if layout == 'force_directed':
            print("Creating force directed graph")
            mapper = EdgeMapper(data, property_key=lens,
                                epsilon=epsilon, num_interval=interval)
            mapper.average = True if mode == 'mean' else False
            data = mapper.cluster
            data = database_api.D3helper.graph_transform(*data)

        elif layout == 'hierarchy':
            print("Creating hierarchy")
            nodes = edges_to_nodes(data)
            tree_mapper = TreeMapper()

            def filter_function(node):
                if lens in node:
                    return node[lens]
                return 0

            # make tree from edges
            hierarchy = tree_mapper.make_tree(
                TreeNode(subreddit, type="subreddit"), nodes)

            # map the edges using default filter function
            cluster = tree_mapper.execute(
                hierarchy, interval, filter_function=filter_function)

            # make tree from mapper nodes
            data = tree_mapper.make_tree(
                TreeNode(subreddit, type="subreddit"), cluster)

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response

    else:
        response = HttpResponse(status=406)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response


@DeprecationWarning
def tree(request, **params):
    import itertools
    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        data = query.get_comments_in_article(article_id)
        nodes = map(lambda py2neo_rel: (
            py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))
        root = TreeNode(article_id)

        hierarchy = TreeMapper().make_tree(root, nodes)
        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=406)


@DeprecationWarning
def tree_map(request, **params):
    import itertools
    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        data = query.get_comments_in_article(article_id)

        # Convert edges to a set of nodes
        nodes = map(lambda py2neo_rel: (
            py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))

        tree_mapper = TreeMapper()
        # Make a tree, using the article node as the root
        root = TreeNode(article_id)
        hierarchy = tree_mapper.make_tree(root, nodes)

        # Run tree mapper on the tree
        tree_mapper.bfs(hierarchy)

        # Make tree from mapper nodes
        root = TreeNode(article_id)
        hierarchy = tree_mapper.make_tree(root, tree_mapper.cluster)

        # Remap mapper nodes x times
        # new_hierarchy = mapXTimes(article_id, hierarchy, times=10)
        return JsonResponse(hierarchy)

    else:
        return HttpResponse(status=406)


@DeprecationWarning
def map_with_tree_mapper(request, **params):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        # grab the article id from the session object and query db
        data = query.get_comments_in_article(article_id)

        # extract the property passed in the url
        lens = 'sentiment_score' if 'lens' not in request.GET else request.GET['lens']

        interval = 6 if 'interval' not in request.GET else int(
            request.GET['interval'])

        epsilon = 0.0 if 'epsilon' not in request.GET else float(
            request.GET['epsilon'])

        mode = 'median' if 'mode' not in request.GET else request.GET['mode']

        # mapper = EdgeMapper(data, property_key=lens, epsilon=epsilon, num_interval=interval)
        # mapper.average = True if mode == 'mean' else False
        # data = mapper.graph()
        # print("Before flattening")
        # print(data)

        # flatten the edge list to node list
        nodes = edges_to_nodes(data)
        tree_mapper = TreeMapper()
        print("Input node count", len(nodes))

        # make tree from edges
        hierarchy = tree_mapper.make_tree(TreeNode(article_id), nodes)
        print("Input Height: {0}".format(tree_mapper.tree_height(hierarchy)))

        # map the edges using default filter function
        cluster = tree_mapper.execute(hierarchy, interval)
        print("Output node count", len(cluster))

        # make tree from mapper nodes
        hierarchy = tree_mapper.make_tree(TreeNode(article_id), cluster)
        print("Output Height: {0}".format(tree_mapper.tree_height(hierarchy)))
        print("Mapper Interval: ", interval)

        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=406)


# Helper functions
def map_x_times(root_id, hierarchy, times=1, function=lambda node: node["value"]):
    """
        run mapper x times on the given hierarchy
        @params:
            - root_id: root node id
            - hierarchy: root
            - times: number of times to run mapper
            - function: filter function

    """
    for _ in range(times):
        root = TreeNode(root_id)
        tree_mapper = TreeMapper()
        tree_mapper.bfs(hierarchy, filter_function=function)
        hierarchy = tree_mapper.make_tree(root, tree_mapper.cluster)

    return hierarchy


def edges_to_nodes(edges):
    """
        flatten edges to nodes
    """
    from collections import defaultdict
    # Convert edges to a set of nodes
    nodes = list(map(lambda edge: (edge.start_node, edge.end_node), edges))
    out = defaultdict()
    for s, e in nodes:
        s['parent_id'] = e['id']
        out[s['id']] = s
        out[e['id']] = e

    return list(out.values())


# Thread tasks
def load_edges_task(*args):
    """
        thread task for loading article graph edges
    """
    article_id, out = args
    out[article_id] = db_layer.get_comments_in_article(article_id)
