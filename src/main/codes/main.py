import matplotlib.pyplot as plt
from json_models import CustomEncoder
from grapher import (Grapher)
import networkx as nx
import graph_writer as gw
import dbimport as dbi

if __name__ == "__main__":
    # the subreddit to scrape
    subreddit = "programming"
    # file name to dumpjson
    filename = "./raw/%s.json" % subreddit

    # create the graphbot that generates both mapper graph and normal graph
    intervals = 10
    prop = "score"
    epsilon = 0.05
    grapher = Grapher(subreddit,"CleverChuk","BwO9pJdzGaVj2pyhZ4kJ", intervals=intervals, property_key=prop, epsilon=epsilon)
    # get data for two submissions in the subreddit
    ids = ["a55xbm","a57th7"]
    # the full graph
    graph = grapher.get_graph(*ids)

    # loader
    loader = dbi.Loader("http://localhost:11002/", "neo4j", "chubi93")

    # load from list
    loader.write_nodes_from_list(grapher.comment_nodes,"comment")
    loader.write_nodes_from_list(grapher.author_nodes,"author")
    loader.write_nodes_from_list(grapher.article_nodes,"article")
    loader.write_nodes_from_list(grapher.sentiment_nodes,"sentiment")

    loader.write_edges_from_list(grapher.comment_comment_edges,type="REPLY_TO")
    loader.write_edges_from_list(grapher.article_comment_edges,type="COMMENTED_IN")
    loader.write_edges_from_list(grapher.author_comment_edges,type="WROTE")
    loader.write_edges_from_list(grapher.sentiment_comment_edges,type="_IS_")

    # load mapper edges from list
    # loader.write_nodes_from_list(grapher.mapper_nodes,"comment")
    # loader.write_edges_from_list(grapher.mapper_edges,type="REPLY_TO")   


    # json dump of the data
    # grapher.dumpjson(filename, ids)

    # write the graphs to files
    # f = "./raw/mapper_comment_nodes.csv"
    # gw.writeNodesToCsv(f, grapher.mapper_nodes)

    # f = "./raw/mapper_comment_edges.csv"
    # gw.writeEdgesToFile(f, grapher.mapper_edges)

    # f = "./raw/comment_nodes.csv"
    # gw.writeNodesToCsv(f, grapher.comment_nodes)

    # f = "./raw/article_nodes.csv"
    # gw.writeNodesToCsv(f, grapher.article_nodes)

    # f = "./raw/sentiment_nodes.csv"
    # gw.writeNodesToCsv(f, grapher.sentiment_nodes)

    # f = "./raw/author_nodes.csv"
    # gw.writeNodesToCsv(f, grapher.author_nodes)

    # gw.writeEdgesToFile("./raw/comment_edges.csv", grapher.comment_comment_edges, directed = True)
    # gw.writeEdgesToFile("./raw/article_comment_edges.csv", grapher.article_comment_edges, directed = True)
    # gw.writeEdgesToFile("./raw/sentiment_comment_edges.csv", grapher.sentiment_comment_edges, directed = True)
    # gw.writeEdgesToFile("./raw/author_comment_edges.csv", grapher.author_comment_edges, directed = True)

    # nx.write_graphml(graph, "./graphML/reddit_graph_%s.graphml" % (subreddit))
    # nx.write_graphml(grapher.comment_graph,"./graphML/comment_graph_%s.graphml" % subreddit)
    # nx.write_graphml(grapher.mapper_graph, "./graphML/%s_intervals_prop_%s.graphml" % (intervals,prop))
