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
        # NOTE: Saving data in session requires that Egde class be JOSN serializable by
        # django serializer
        data = query.get_comments_in_article(param["id"])
        mapper_edges = list(map(Edge.cast, data))
        data = database_api.D3helper.transform(*data)

        return JsonResponse(data)


def mapper_graph(request):
    global mapper_edges
    if request.method == "GET":
        # grab the article id from the session object and query db
        if mapper_edges is None or not len(mapper_edges):
            data = query.get_comments_in_article(request.session[ARTICLE_ID])
            mapper_edges = list(map(Edge.cast, data))

        if request.GET:
            # extract the property passed in the url
            if 'prop' in request.GET:
                prop = request.GET['prop']
            else:
                prop = 'reading_level'

            if 'interval' in request.GET:
                interval = int(request.GET['interval'])
            else:
                interval = 3

            if 'epsilon' in request.GET:
                epsilon = float(request.GET['epsilon'])
            else:
                epsilon = 0.5

            if 'mode' in request.GET:
                mode = request.GET['mode']
            else:
                mode = 'median'

            mapper = EdgeMapper(mapper_edges, property_key=prop,
                                epsilon=epsilon, num_interval=interval)

            mapper.average = True if mode == 'mean' else False
            data = mapper.cluster()
        else:
            data = EdgeMapper(mapper_edges).cluster()

        data = database_api.D3helper.transform(*data)

        return JsonResponse(data)


def tree(request, **params):
    import itertools
    if (request.method == "GET") and "id" in params:
        article_id = params["id"]
        data = query.get_comments_in_article(article_id)

        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))
        root = TreeNode(article_id)

        hierarchy = root.make_tree(root, nodes)
        return JsonResponse(hierarchy)
    else:
        return HttpResponse(status=404)


def tree_map(request, **params):
    import itertools
    if (request.method == "GET") and "id" in params:
        article_id = params["id"]
        data = query.get_comments_in_article(article_id)

        # Convert edges to a set of nodes
        nodes = map(lambda py2neo_rel: (py2neo_rel.start_node, py2neo_rel.end_node), data)
        nodes = set(itertools.chain(*nodes))

        # Make a tree, using the article node as the root        
        root = TreeNode(article_id)
        hierarchy = TreeNode.make_tree(root, nodes)
        
        # Run tree mapper on the tree
        tree_mapper = TreeMapper(hierarchy)
        tree_mapper.bfs()
        
        # Make tree from mapper nodes
        root = TreeNode(article_id)
        hierarchy = TreeNode.make_tree(root, tree_mapper.cluster)
        
        # Remap mapper nodes x times
        new_hierarchy = map_x_times(article_id, hierarchy, times = 10)
        
        return JsonResponse(new_hierarchy)
    
    else:
        return HttpResponse(status=404)


# Helper functions
def get_equal(field, value):
    data = query.get_equal(field, value)
    return data

def map_x_times(root_id, hierarchy, times = 1, function= lambda node: node["value"]):
    for _ in range(times):
        root = TreeNode(root_id)
        tree_mapper = TreeMapper(hierarchy)
        tree_mapper.bfs(filter_function = function)
        hierarchy = TreeNode.make_tree(root, tree_mapper.cluster)
      

    return hierarchy