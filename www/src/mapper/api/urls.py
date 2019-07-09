from django.urls import path
from . import views

# paths in this app
urlpatterns = [
    path('all', views.all, name='all'),
    path('rels/<str:type>', views.relationship, name='rels'),
    path('nodes', views.get_nodes, name='nodes'),
    path('nodes/<str:label>', views.node_label, name='node_label'),    
    path('nodes/article/<str:id>', views.nodes_in_article, name='nodes_in_article'),

    path('nodes/<str:field>/<str:value>', views.equal_str, name='equal_string'),
    path('nodes/<str:field>/equal/<str:value>', views.equal, name='equal'),
    path('nodes/<str:field>/greater/<str:value>', views.greater, name='greater'),
    path('nodes/<str:field>/greator/<str:value>', views.greater_or_equal, name='greater_or_equal'),
    path('nodes/<str:field>/less/<str:value>', views.less, name='less'),
    path('nodes/<str:field>/lessor/<str:value>', views.less_or_equal, name='lesser_or_equal'),

    path('mapper', views.mapper_graph, name='mapper_graph'),
    path('subreddit', views.subreddit_graph, name='subreddit'),
    
    # Tree endpoints
    path("tree/<str:id>", views.tree_map, name="tree"),
]
