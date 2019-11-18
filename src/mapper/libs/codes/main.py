import db_loaders as dbl
import graph_writers as gws
from reddit_crawler import (Crawler)
import json
import threading


def download_task(*args, **kwargs):
    crawler = Crawler(subreddit, credential)
    # get data for two submissions in the subreddit
    # ids = crawler.get_hot_submissions(2)
    crawler.get_graph(*args)
    # loader
    loader = dbl.Neo4jLoader("http://localhost:11002/", "neo4j", "chubi93")

    # load from list
    loader.write_nodes_from_list(crawler.comment_nodes, "comment")
    loader.write_nodes_from_list(crawler.author_nodes, "author")
    loader.write_nodes_from_list(crawler.article_nodes, "article")
    loader.write_nodes_from_list(crawler.sentiment_nodes, "sentiment")
    loader.write_nodes_from_list([crawler.subreddit_node], "subreddit")

    loader.write_edges_from_list(crawler.comment_comment_edges, type="REPLY_TO")
    loader.write_edges_from_list(crawler.article_comment_edges, type="COMMENTED_IN")
    loader.write_edges_from_list(crawler.author_comment_edges, type="WROTE")
    loader.write_edges_from_list(crawler.sentiment_comment_edges, type="_IS_")
    loader.write_edges_from_list(crawler.article_subreddit_edges, type="_IN_")


if __name__ == "__main__":
    # the subreddit to scrape
    # subreddit = "programming"
    subreddit = "politics"
    # file name to dumpjson
    filename = "./raw/%s.json" % subreddit
    with open("./credential.json", "r") as fp:
        lines = "".join(fp.readlines())
        credential = json.loads(lines)
        crawler = Crawler(subreddit, credential)
        # get data for two submissions in the subreddit
        ids = list(crawler.get_hot_submissions(10))

    n = len(ids)
    step = n // 3
    threads = []
    for i in range(0, n, step):
        t = threading.Thread(target=download_task, args=ids[i:i + step])
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
