import matplotlib.pyplot as plt
from json_models import CustomEncoder
from reddit_crawler import (Crawler)
import networkx as nx
import graph_writers as gws
import db_loaders as dbl

if __name__ == "__main__":
    gw = gws.Neo4jGrapher()
    # the subreddit to scrape
    subreddit = "programming"
    # file name to dumpjson
    filename = "./raw/%s.json" % subreddit

    # create the graphbot that generates both mapper graph and normal graph
    intervals = 10
    prop = "score"
    epsilon = 0.05
    crawler = Crawler(subreddit,"CleverChuk","BwO9pJdzGaVj2pyhZ4kJ", intervals=intervals, property_key=prop, epsilon=epsilon)
    # get data for two submissions in the subreddit
    ids = crawler.get_submissions()
    # ids = crawler.get_hot_submissions(2)
    crawler.get_graph(*ids)

    # loader
    loader = dbl.Neo4jLoader("http://localhost:11002/", "neo4j", "chubi93")

    # load from list
    loader.write_nodes_from_list(crawler.comment_nodes,"comment")
    loader.write_nodes_from_list(crawler.author_nodes,"author")
    loader.write_nodes_from_list(crawler.article_nodes,"article")
    loader.write_nodes_from_list(crawler.sentiment_nodes,"sentiment")

    loader.write_edges_from_list(crawler.comment_comment_edges,type="REPLY_TO")
    loader.write_edges_from_list(crawler.article_comment_edges,type="COMMENTED_IN")
    loader.write_edges_from_list(crawler.author_comment_edges,type="WROTE")
    loader.write_edges_from_list(crawler.sentiment_comment_edges,type="_IS_")