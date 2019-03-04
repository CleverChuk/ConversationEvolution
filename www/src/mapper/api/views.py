from django.shortcuts import render
from django.http import JsonResponse
from libs import api
from .models import *
from .mapper import EdgeMapper, Edge

context = {}
mapper_edges = []
# Create db layer object and pass it query object
db_layer = api.Neo4jLayer()
query = api.Query(db_layer)

# Create your views here.


def all(request):
    if(request.method == "GET"):
        data = query.all()
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
        id = param["id"]
        data = query.get_nodes_in_article(id)
        mapper_edges = map(Edge.cast, data)

        data = api.D3helper.transform(*data)
        print(data)
        return JsonResponse(data)


def mapper_graph(request):
    global mapper_edges
    if(request.method == "GET"):
        data = EdgeMapper(list(mapper_edges)).cluster()
        data = api.D3helper.transform(*data)
        return JsonResponse(data)


# Helper functions
def get_nodes(label):
    data = query.get_nodes_by_label(label)
    context = {"nodes": data}
    return JsonResponse(context)


def get_equal(field, value):
    data = query.get_equal(field, value)
    return data
