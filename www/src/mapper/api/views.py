from django.shortcuts import render
from django.http import JsonResponse
from libs import api
from .models import *
from .mapper import EdgeMapper, Edge

# constants
ARTICLE_ID = 'article_id'
# Create db layer object and pass it to the query object
db_layer = api.Neo4jLayer()
query = api.Query(db_layer)

# global variables
context = {}
mapper_edges = None


# Create your views here.


def all(request):
    """
        reads the how graph from database
    """
    if(request.method == "GET"):
        data = query.all()
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def subreddit_graph(request):
    if(request.method == "GET"):
        data = query.get_subreddit_graph()
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def nodes(request, **param):
    if(request.method == "GET"):
        queryset = request.GET
        if queryset:
            for f, v in queryset.items():
                context[f] = api.D3helper.transform(*get_equal(f, v))
            return JsonResponse(context)

        context["graph"] = query.nodes()
        return JsonResponse(context)


def node_label(request, **param):
    return get_nodes(param["label"])


def relationship(request, **param):
    if(request.method == "GET"):
        data = query.get_relationship_by_type(param["type"])
        data = api.D3helper.transform(*data)

        return JsonResponse(data)


def equal_str(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_equal_str(field, value)
        data = api.D3helper.transform(*data)

        return JsonResponse(data)


def equal(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_equal(field, value)
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def greater(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_greater(field, value)
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def greater_or_equal(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_greater_or_equal(field, value)
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def less(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_less(field, value)
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def less_or_equal(request, **param):
    if(request.method == "GET"):
        field = param["field"]
        value = param["value"]

        data = query.get_less_or_equal(field, value)
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


def nodes_in_article(request, **param):
    global mapper_edges
    if(request.method == "GET"):
        # add article id to session object
        request.session[ARTICLE_ID] = param["id"]
        # NOTE: Saving data in session requires that Egde class be JOSN serializable by
        # django serializer
        data = query.get_nodes_in_article(param["id"])
        mapper_edges = list(map(Edge.cast, data))
        data = api.D3helper.transform(*data)

        return JsonResponse(data)


def mapper_graph(request):
    global mapper_edges
    if(request.method == "GET"):
        # grab the article id from the session object and query db
        if mapper_edges == None or not len(mapper_edges):
            data = query.get_nodes_in_article(request.session[ARTICLE_ID])
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

        data = api.D3helper.transform(*data)

        print([interval, epsilon, mode])
        return JsonResponse(data)

# Helper functions


def get_nodes(label):
    data = query.get_nodes_by_label(label)
    context = {"nodes": data}
    return JsonResponse(context)


def get_equal(field, value):
    data = query.get_equal(field, value)
    return data
