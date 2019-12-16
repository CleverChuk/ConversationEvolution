import db_loaders as dbl
import graph_writers as gws
from reddit_crawler import (Crawler)
import json
import threading
import os
cur_dir = os.path.dirname(__file__)
NEO4J_URL = os.environ["NEO4J_URL"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
print("="*100)
print(f"{NEO4J_URL}, {NEO4J_USERNAME}, {NEO4J_PASSWORD}")   
print("="*100)

def download_task(*args, **kwargs):
    sub = kwargs['sub']
    crawler = Crawler(sub, credential)
    # get data for two submissions in the subreddit
    # ids = crawler.get_hot_submissions(2)
    crawler.get_graph(*args)
    # loader
    loader = dbl.Neo4jLoader(NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD)

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

    print(f"""Wrote {sum([len(l) for l in 
        [
            crawler.comment_nodes,
            crawler.author_nodes,
            crawler.article_nodes,
            crawler.sentiment_nodes,
            [crawler.subreddit_node]
        ]
    ])} nodes and {sum([len(r) for r in 
        [
            crawler.comment_comment_edges,
            crawler.article_comment_edges,
            crawler.author_comment_edges,
            crawler.sentiment_comment_edges,
            crawler.article_subreddit_edges
        ]
    ])} edges to database.""")


if __name__ == "__main__":
    # the subreddits to scrape
    subreddits = ["legaladvice", "programming", "politics"]
    with open(f"credential.json", "r") as fp:
        lines = "".join(fp.readlines())
        credential = json.loads(lines)
        crawler = Crawler(None, credential)
        # get data for two submissions in the subreddit
        submissions = [(list(crawler.get_hot_submissions(sub_red=sub_red,limit=10)),sub_red) for sub_red in subreddits]

        
    threads = []
    for ids, sub  in submissions:
        n = len(ids)
        step = n // 2
        for i in range(0, n, step):
            t = threading.Thread(target=download_task, args=ids[i:i + step], kwargs={"sub":sub})
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
