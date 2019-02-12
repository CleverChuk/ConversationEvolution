from django.shortcuts import render
from django.http import JsonResponse
from libs import api

db_layer = api.Neo4jLayer()
query = api.Query(db_layer)

# Create your views here.
def all(request):
    if(request.method == "GET"):
        data = query.all()
        data = api.D3helper.transform(*data)
        data = api.D3helper.dumpsJSON(data)

        context = {"graph":data}
        
        return JsonResponse(context)