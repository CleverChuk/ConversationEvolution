from django.shortcuts import render
from libs import api

# Create your views here.
def index(request):
    return render(request,"main/viz.html")
