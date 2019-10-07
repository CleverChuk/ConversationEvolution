from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from libs import database_api
from .models import *
from .mapper import EdgeMapper, Edge, TreeMapper

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
    if request.method == "GET":
        data = query.all()
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def subreddit_graph(request):
    if request.method == "GET":
        data = query.get_subreddit_graph()
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def get_nodes(request):
    if request.method == "GET":
        queryset = request.GET
        if queryset:
            for f, v in queryset.items():
                context[f] = database_api.D3helper.graph_transform(*get_equal(f, v))
            return JsonResponse(context)

        context["graph"] = query.nodes()
        return JsonResponse(context)
    else:
        return HttpResponse(status=403)


def node_label(request, **param):
    label = param.get("label", None)
    if request.method == "GET" and label:
        data = query.get_nodes_by_label(label)
        return JsonResponse({"nodes": data})
    else:
        return HttpResponse(status=403)


def relationship(request, **param):
    _type = param.get("type", None)
    if request.method == "GET" and _type:
        data = query.get_relationship_by_type(_type)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def equal_str(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:
        data = query.get_equal_str(field, value)
        data = database_api.D3helper.graph_transform(*data)

        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def equal(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def greater(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_greater(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def greater_or_equal(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_greater_or_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def less(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:
        data = query.get_less(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def less_or_equal(request, **param):
    field = param.get("field", None)
    value = param.get("value", None)
    if request.method == "GET" and field and value:

        data = query.get_less_or_equal(field, value)
        data = database_api.D3helper.graph_transform(*data)
        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


def nodes_in_article(request, **param):
    global mapper_edges
    article_id = param.get("id", None)
    if request.method == "GET" and article_id:
        # add article id to session object
        request.session[ARTICLE_ID] = article_id
        # NOTE: Saving data in session requires that Edge class be JSON serializable by
        # django serializer
        data = query.get_comments_in_article(article_id)
        # mapper_edges = list(map(Edge.cast, data))
        # data = database_api.D3helper.transform(*data)

        # Return tree graph
        nodes = edges_to_nodes(data)
        tree_mapper = TreeMapper()
        root = TreeNode(article_id)

        # make tree from edges
        hierarchy = tree_mapper.make_tree(root, nodes)
        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=403)


def get_articles(request):
    if request.method == "GET":
        data = query.get_all_articles()
        return JsonResponse({"data": data})
    return HttpResponse(status=403)


def get_articles_in_subreddit(request, **params):
    if request.method == "GET":
        subreddit = params.get("subreddit", None)
        if subreddit:
            data = query.get_articles_in_subreddit(subreddit)
            return JsonResponse({"data": data})
        else:
            return HttpResponse(status=400)

    return HttpResponse(status=403)


def get_edges_in_subreddit(request):
    if request.method == "GET":
        subreddit = request.GET.get("subreddit", None)
        if subreddit:
            data = query.get_edges_in_subreddit(subreddit)
            data = database_api.D3helper.graph_transform(*data)
            response = JsonResponse({"data": data})
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "*"

            return response
        else:
            return HttpResponse(status=400)

    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "*"
        return response

    return HttpResponse(status=403)


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

        data = database_api.D3helper.graph_transform(*data)

        return JsonResponse(data)
    else:
        return HttpResponse(status=403)


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
        return HttpResponse(status=403)


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
        return HttpResponse(status=403)


def map_with_tree_mapper(request, **params):
    article_id = params.get("id", None)
    if (request.method == "GET") and article_id:
        # grab the article id from the session object and query db
        data = query.get_comments_in_article(article_id)

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
        return HttpResponse(status=403)


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

    return out.values()
