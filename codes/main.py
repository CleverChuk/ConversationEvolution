import matplotlib.pyplot as plt
from json_models import CustomEncoder
from grapher import (GraphBot)
import networkx as nx
import graph_writer as gw

if __name__ == "__main__":
    subreddit = "legaladvice"
    filename = "./raw/%s.json" % subreddit

    grapher = GraphBot(subreddit)
    ids = list(grapher.get_hot_submissions_id(2))
    graph = grapher.getGraph(*ids)
    
    # write files
    grapher.dump(filename, ids)
        
    f = "./raw/mapper_comment_data.csv"
    gw.writeNodesToCsv(f, grapher.mapper_nodes)

    f = "./raw/mapper_comment_edge_data.csv"
    gw.writeEdgesToFile(f, grapher.mapper_edges)

    f = "./raw/comment_nodes.csv"
    gw.writeNodesToCsv(f, grapher.comment_nodes)

    f = "./raw/article_nodes.csv"
    gw.writeNodesToCsv(f, grapher.article_nodes)
    
    f = "./raw/sentiment_nodes.csv"
    gw.writeNodesToCsv(f, grapher.sentiment_nodes)
        
    f = "./raw/author_nodes.csv"
    gw.writeNodesToCsv(f, grapher.author_nodes)

    gw.writeEdgesToFile("./raw/comment_edge_data.csv", grapher.comment_comment_edges, directed = True)
    gw.writeEdgesToFile("./raw/article_comment_edge_data.csv", grapher.article_comment_edges, directed = True)
    gw.writeEdgesToFile("./raw/sentiment_comment_edge_data.csv", grapher.sentiment_comment_edges, directed = True)
    gw.writeEdgesToFile("./raw/author_comment_edge_data.csv", grapher.author_comment_edges, directed = True)

    nx.write_graphml(graph, "./graphML/reddit_graph_%s.graphml" % subreddit)
    nx.write_graphml(grapher.comment_graph,"./graphML/comment_graph_%s.graphml" % subreddit)
    nx.write_graphml(grapher.mapper_graph, "./graphML/interval_graph_edges.graphml")