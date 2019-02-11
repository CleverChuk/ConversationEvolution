from django.urls import path
from . import views

# paths in this app
urlpatterns = [
    path('', views.index, name='index'),
]