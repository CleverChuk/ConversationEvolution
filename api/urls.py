from django.urls import path
from . import views

# paths in this app
urlpatterns = [
    path('all', views.all_nodes, name='all'),
    path('rels/<str:type>', views.get_relationship_by_type, name='rels'),
    path('nodes', views.get_nodes, name='nodes'),
    path('nodes/<str:label>', views.get_nodes_by_label, name='get_nodes_by_label'),
    path('article/nodes', views.get_edges_in_article, name='nodes_in_article'),

    path('nodes/<str:field>/<str:value>', views.equal_str, name='equal_string'),
    path('nodes/<str:field>/equal/<str:value>', views.equal, name='equal'),
    path('nodes/<str:field>/greater/<str:value>', views.greater, name='greater'),
    path('nodes/<str:field>/greator/<str:value>', views.greater_or_equal, name='greater_or_equal'),
    path('nodes/<str:field>/less/<str:value>', views.less, name='less'),
    path('nodes/<str:field>/lessor/<str:value>', views.less_or_equal, name='lesser_or_equal'),

    path("articles", views.get_all_article, name='articles'),
    path("articles/<str:subreddit>", views.get_articles_in_subreddit, name='articles'),

    path("subreddit", views.get_edges_in_subreddit, name='subreddit'),
    # path('mapper', views.mapper_graph, name='mapper_graph'),
    path('lenses', views.get_topological_lens, name="lens"),

    # Tree endpoints
    # path("tree/<str:id>", views.map_with_tree_mapper, name="tree"),
]
