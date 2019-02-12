from django.urls import path
from . import views

# paths in this app
urlpatterns = [
    path('all', views.all, name='all'),
    path('', views.all, name='all'),
]