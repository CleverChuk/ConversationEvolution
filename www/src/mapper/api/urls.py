from django.urls import path
from . import views

# paths in this app
urlpatterns = [
    path('graph', views.graph, name='graph'),
    path('', views.graph, name='graph'),
]