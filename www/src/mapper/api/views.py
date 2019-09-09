from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from libs import database_api
from .models import *
from .mapper import EdgeMapper, Edge, TreeMapper

# constants
ARTICLE_ID = 'articleId'
# Create db layer object and pass it to the query object
db_layer = database_api.Neo4jLayer()
query = database_api.Query(db_layer)

# global variables
context = {}
mapper_edges = None


# Create your views here.


def all(request):
    """
        reads the how graph from database
    """
    if request.method == "GET":
        data = query.all()
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def subreddit_graph(request):
    if request.method == "GET":
        data = query.get_subreddit_graph()
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def get_nodes(request):
    if request.method == "GET":
        queryset = request.GET
        if queryset:
            for f, v in queryset.items():
                context[f] = database_api.D3helper.transform(*get_equal(f, v))
            return JsonResponse(context)

        context["graph"] = query.nodes()
        return JsonResponse(context)


def node_label(request, **param):
    data = query.get_nodes_by_label(param["label"])
    context = {"nodes": data}
    return JsonResponse(context)


def relationship(request, **param):
    if request.method == "GET":
        data = query.get_relationship_by_type(param["type"])
        data = database_api.D3helper.transform(*data)

        return JsonResponse(data)


def equal_str(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_equal_str(field, value)
        data = database_api.D3helper.transform(*data)

        return JsonResponse(data)


def equal(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_equal(field, value)
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def greater(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_greater(field, value)
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def greater_or_equal(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_greater_or_equal(field, value)
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def less(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_less(field, value)
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def less_or_equal(request, **param):
    if request.method == "GET":
        field = param["field"]
        value = param["value"]

        data = query.get_less_or_equal(field, value)
        data = database_api.D3helper.transform(*data)
        return JsonResponse(data)


def nodes_in_article(request, **param):
    global mapper_edges
    if request.method == "GET":
        # add article id to session object
        request.session[ARTICLE_ID] = param["id"]
        # NOTE: Saving data in session requires that Edge class be JSON serializable by
        # django serializer
        data = query.get_comments_in_article(param["id"])
        # mapper_edges = list(map(Edge.cast, data))
        # data = database_api.D3helper.transform(*data)

        # Return tree graph
        nodes = edgesToNodes(data)
        treeMapper = TreeMapper()
        root = TreeNode(param["id"])

        # make tree from edges
        hierarchy = treeMapper.makeTree(root, nodes)
        return JsonResponse(hierarchy)


def mapper_graph(request):
    global mapper_edges
    if request.method == "GET":
        # grab the article id from the session object and query db
        if mapper_edges is None or not len(mapper_edges):
            data = query.get_comments_in_article(request.session[ARTICLE_ID])
            mapper_edges = list(map(Edge.cast, data))

        # extract the property passed in the url
        prop = 'reading_level' if 'prop' not in request.GET else request.GET['prop']

        interval = 3 if 'interval' not in request.GET else int(request.GET['interval'])

        epsilon = 0.5 if 'epsilon' not in request.GET else float(request.GET['epsilon'])

        mode = 'median' if 'mode' not in request.GET else request.GET['mode']

        mapper = EdgeMapper(mapper_edges, property_key=prop, epsilon=epsilon, num_interval=interval)
        mapper.average = True if mode == 'mean' else False
        data = mapper.cluster

        data = database_api.D3helper.transform(*data)

        return JsonResponse(data)


def tree(request, **params):
    import itertools
    if (request.method == "GET") and "id" in params:
        articleId = params["id"]
        data = query.get_comments_in_article(articleId)

        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))
        root = TreeNode(articleId)

        hierarchy = TreeMapper().makeTree(root, nodes)
        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=404)


def tree_map(request, **params):
    import itertools
    if (request.method == "GET") and "id" in params:
        articleId = params["id"]
        data = query.get_comments_in_article(articleId)

        # Convert edges to a set of nodes
        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))

        treeMapper = TreeMapper()
        # Make a tree, using the article node as the root
        root = TreeNode(articleId)
        hierarchy = treeMapper.makeTree(root, nodes)

        # Run tree mapper on the tree
        treeMapper.bfs(hierarchy)

        # Make tree from mapper nodes
        root = TreeNode(articleId)
        hierarchy = treeMapper.makeTree(root, treeMapper.cluster)

        # Remap mapper nodes x times
        # new_hierarchy = mapXTimes(articleId, hierarchy, times=10)
        return JsonResponse(hierarchy)

    else:
        return HttpResponse(status=404)


def tree_mapper(request, **params):
    if (request.method == "GET") and "id" in params:
        articleId = params["id"]
        # grab the article id from the session object and query db
        data = query.get_comments_in_article(articleId)

        # extract the property passed in the url
        prop = 'sentiment_score' if 'prop' not in request.GET else request.GET['prop']

        interval = 6 if 'interval' not in request.GET else int(request.GET['interval'])

        epsilon = 0.0 if 'epsilon' not in request.GET else float(request.GET['epsilon'])

        mode = 'median' if 'mode' not in request.GET else request.GET['mode']

        # mapper = EdgeMapper(data, property_key=prop, epsilon=epsilon, num_interval=interval)
        # mapper.average = True if mode == 'mean' else False
        # data = mapper.graph()
        # print("Before flattening")
        # print(data)

        # flatten the edge list to node list
        nodes = edgesToNodes(data)
        treeMapper = TreeMapper()
        print("Input node count", len(nodes))

        # make tree from edges
        hierarchy = treeMapper.makeTree(TreeNode(articleId), nodes)
        print("Input Height: {0}".format(treeMapper.treeHeight(hierarchy)))

        # map the edges using default filter function      
        cluster = treeMapper.execute(hierarchy, interval)
        print("Output node count", len(cluster))

        # make tree from mapper nodes
        hierarchy = treeMapper.makeTree(TreeNode(articleId), cluster)
        print("Output Height: {0}".format(treeMapper.treeHeight(hierarchy)))
        print("Mapper Interval: ", interval)

        return JsonResponse(hierarchy)


# Helper functions
def get_equal(field, value):
    data = query.get_equal(field, value)
    return data


def mapXTimes(root_id, hierarchy, times=1, function=lambda node: node["value"]):
    for _ in range(times):
        root = TreeNode(root_id)
        treeMapper = TreeMapper()
        treeMapper.bfs(hierarchy, filter_function=function)
        hierarchy = treeMapper.makeTree(root, treeMapper.cluster)

    return hierarchy


def edgesToNodes(edges):
    from collections import defaultdict
    # Convert edges to a set of nodes
    nodes = list(map(lambda edge: (edge.start_node, edge.end_node), edges))
    out = defaultdict()
    for s, e in nodes:
        s['parent_id'] = e['id']
        out[s['id']] = s
        out[e['id']] = e

    return out.values()
