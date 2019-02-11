from django.shortcuts import render
from django.http import JsonResponse
from libs import api

# Create your views here.
def graph(request):
    data = api.Query().all()
    data = api.D3helper.transform(*data)
    data = api.D3helper.dumpsJSON(data)

    context = {"graph":data}
    return JsonResponse(context)