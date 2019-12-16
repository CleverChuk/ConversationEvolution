from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from libs import database_api
from .models import *
from .mapper import EdgeMapper, Edge, TreeMapper
import json
import threading
import numpy as np
import os

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

# global variables
context = {}
mapper_edges = None


# Create your views here.


def all_nodes(request):
    """
        reads the how graph from database
    """
    if request.method == "OPTIONS":
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


def subreddit_graph(request):
    if request.method == "GET":
        data = query.get_subreddit_graph()
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def get_nodes(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"
        return response

    if request.method == "GET":
        queryset = request.GET
        if queryset:
            for f, v in queryset.items():
                context[f] = database_api.D3helper.graph_transform(*get_equal(f, v))
            return JsonResponse(context)

        context["graph"] = query.nodes()
        return JsonResponse(context)
    else:
        return HttpResponse(status=406)


def node_label(request, **param):
    if request.method == "OPTIONS":
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


def relationship(request, **param):
    _type = param.get("type", None)
    if request.method == "GET" and _type:
        data = query.get_relationship_by_type(_type)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=406)


def equal_str(request, **param):
    if request.method == "OPTIONS":
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
    if request.method == "OPTIONS":
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
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Headers"] = request.META["HTTP_ACCESS_CONTROL_REQUEST_HEADERS"]
        response["Access-Control-Allow-Methods"] = "POST"
        response["Access-Control-Allow-Origin"] = "*"

        return response

    if request.method == "POST":
        # todo Handle empty body and missing param error
        body = json.loads(request.body)
        print(body)
        ids = body["ids"]
        is_mapper = body["mapper"]

        if ids:
            data = {}
            threads = []

            for id in ids:
                t = threading.Thread(target=load_edges_task, args=(id, data))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            if body['layout'] == 'hierarchy':
                _tree = TreeNode("root", type="root")
                if is_mapper:
                    for i in range(len(data)):
                        # run mapper on each article graph
                        _tree.add_child(_mapper_hierarchy(data[ids[i]], ids[i], "article", **body["m_params"]))
                else:
                    for i in range(len(data)):
                        _tree.add_child(_hierarchy(data[ids[i]], ids[i], "article"))

                response = JsonResponse(_tree)
                response["Content-type"] = 'application/json'
                response["Access-Control-Allow-Origin"] = "*"
                return response

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
                data = tree_mapper.make_tree(TreeNode(subreddit, type="subreddit"), nodes)

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
    # extract the query passed in the url
    lens = 'reading_level' if 'lens' not in params else params['lens']
    interval = 3 if 'interval' not in params else int(params['interval'])
    epsilon = 0.5 if 'epsilon' not in params else float(params['epsilon'])

    mode = 'median' if 'mode' not in params else params['mode']
    algorithm = 'cc' if 'clustering_algorithm' not in params else params[
        'clustering_algorithm']  # no implementation for this yet

    print("Creating force directed graph")
    mapper = EdgeMapper(data, property_key=lens, epsilon=epsilon, num_interval=interval)
    mapper.average = True if mode == 'mean' else False
    return database_api.D3helper.graph_transform(*mapper.cluster)


def _mapper_hierarchy(data, root_id, root_type, **params):
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
    cluster = tree_mapper.execute(hierarchy, interval, filter_function=filter_function)

    # make tree from mapper nodes
    return tree_mapper.make_tree(TreeNode(root_id, type=root_type), cluster)


def _hierarchy(data, root_id, root_type):
    print("Creating hierarchy")
    nodes = edges_to_nodes(data)
    tree_mapper = TreeMapper()

    root = TreeNode(root_id, type=root_type)
    root["comment_count"] = len(nodes)
    # make tree from edges
    return tree_mapper.make_tree(root, nodes)


def mapper_graph(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response

    elif request.method == "GET":
        # extract the query passed in the url
        lens = 'reading_level' if 'lens' not in request.GET else request.GET['lens']
        interval = 3 if 'interval' not in request.GET else int(request.GET['interval'])
        epsilon = 0.5 if 'epsilon' not in request.GET else float(request.GET['epsilon'])

        mode = 'median' if 'mode' not in request.GET else request.GET['mode']
        layout = 'hierarchy' if 'graph_layout' not in request.GET else request.GET['graph_layout']
        algorithm = 'cc' if 'clustering_algorithm' not in request.GET else request.GET[
            'clustering_algorithm']  # no implementation for this yet
        subreddit = 'legaladvice' if 'subreddit' not in request.GET else request.GET['subreddit']
        data = db_layer.get_edges_in_subreddit(subreddit)

        print("Params", request.GET)
        if layout == 'force_directed':
            print("Creating force directed graph")
            mapper = EdgeMapper(data, property_key=lens, epsilon=epsilon, num_interval=interval)
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
            hierarchy = tree_mapper.make_tree(TreeNode(subreddit, type="subreddit"), nodes)

            # map the edges using default filter function
            cluster = tree_mapper.execute(hierarchy, interval, filter_function=filter_function)

            # make tree from mapper nodes
            data = tree_mapper.make_tree(TreeNode(subreddit, type="subreddit"), cluster)

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response

    else:
        response = HttpResponse(status=406)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET"

        return response


def tree(request, **params):
    import itertools
    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        data = query.get_comments_in_article(article_id)
        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))
        root = TreeNode(article_id)

        hierarchy = TreeMapper().make_tree(root, nodes)
        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=406)


def tree_map(request, **params):
    import itertools
    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        data = query.get_comments_in_article(article_id)

        # Convert edges to a set of nodes
        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
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

        interval = 6 if 'interval' not in request.GET else int(request.GET['interval'])

        epsilon = 0.0 if 'epsilon' not in request.GET else float(request.GET['epsilon'])

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
def get_equal(field, value):
    data = query.get_equal(field, value)
    return data


def map_x_times(root_id, hierarchy, times=1, function=lambda node: node["value"]):
    for _ in range(times):
        root = TreeNode(root_id)
        tree_mapper = TreeMapper()
        tree_mapper.bfs(hierarchy, filter_function=function)
        hierarchy = tree_mapper.make_tree(root, tree_mapper.cluster)

    return hierarchy


def edges_to_nodes(edges):
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
    article_id, out = args
    out[article_id] = db_layer.get_comments_in_article(article_id)
