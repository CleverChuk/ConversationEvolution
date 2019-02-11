from django.shortcuts import render
from libs import api

# Create your views here.
def index(request):
    data = api.Query().all()
    data = api.D3helper.transform(*data)
    data = api.D3helper.dumpsJSON(data)

    context = {"graph":data}
    return render(request,"main/viz.html", context)
