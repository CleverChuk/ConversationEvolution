# Author: Chukwubuikem Ume-Ugwa
# Purpose: Class use to generate a graph from pulled data
from networkx import (Graph, DiGraph, read_graphml)
from analyzers import CommentAnalyzer
from textsim import cosine_sim
from models import CommentNode, AuthorNode, Node, ArticleNode, SentimentNode
from base_crawler import RedditBot


class Crawler(RedditBot):
    """
        A subclass of RedditBot that can be used to build mapper graph
    """
    relationship_id = 0

    def __init__(self, subreddit, credentials, property_key="sentiment_score", epsilon=0.5, intervals=3,
                 app_name="myapp", version="1.0.0"):
        """
        Builds the GraphBot objects using default or provided configuration

        @param subreddit
            :type string
            :description: the name of the subreddit to get data from

        @param username
            :type string
            :description: Reddit username

        @param password
            :type string
            :description: Reddit password

        @param property_key
            :type string
            :description: the comment property used to build the mapper graph

        @param intervals
            :type int
            :description: the number intervals used for the mapper graph

        @param epsilon
            :type float
            :description: how much to shift the property_key to create overlap
        """
        super().__init__(subreddit, credentials, VERSION=version, APP_NAME=app_name)
        self.property_key = property_key
        self.epsilon = epsilon
        self.intervals = intervals

        self.article_comment_edges = []  # article/comment edge
        self.comment_comment_edges = []  # undirected comment/comment edges
        self.sentiment_comment_edges = []  # sentiment/comment edges
        self.author_comment_edges = []  # author/comment edges
        self.article_subreddit_edges = []

        self.nodes = []
        self.comment_nodes = []
        self.article_nodes = []
        self.sentiment_nodes = []
        self.author_nodes = []
        self.subreddit_node = Node(
            {'id': subreddit, "type": "subreddit", "name": subreddit})

    def is_removed(self, comment):
        """
            return true if the comment has been removed otherwise false

            @param comment
                :type CommentNode
                :description: comment node object
        """
        return comment.body == "[removed]" or "*Your post has been removed for the following reason(s):*" in comment.body

    def stream(self, subreddit):
        """
            streams graphs from the given subreddit 

            @param: subreddit
                    :type string
                    :description: subreddit name
        """
        stream = self.reddit.subreddit(subreddit).stream
        for submission in stream.submissions():
            yield self.get_graph(submission.id)

    def get_graph(self, *ids):
        """"
            builds graph from article with submission id

            @param *ids: 
                :type list
                :description: list of submission ids in the subreddit

            :rtype Graph
        """
        self.ids = ids  # save the ids for future queries
        sentiment = {
            "positive": SentimentNode(self.subreddit_tag, "positive"),
            "negative": SentimentNode(self.subreddit_tag, "negative"),
            "neutral": SentimentNode(self.subreddit_tag, "neutral")
        }

        # add the sentiment nodes to the node list
        for _, v in sentiment.items():
            self.sentiment_nodes.append(v)
            self.nodes.append((v, v))

        for id in ids:
            try:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)
                article_node = ArticleNode(self.subreddit_tag, submission)

                self.article_subreddit_edges.append(
                    (article_node, self.subreddit_node))
                self.nodes.append((article_node, article_node))
                self.article_nodes.append(article_node)

                # populate article/comment edge list
                for comment in submission.comments.list():
                    comment_node = CommentNode(
                        self.subreddit_tag, article_node['id'], comment, CommentAnalyzer(comment))
                    author_node = AuthorNode(
                        self.subreddit_tag, comment_node['author'])

                    self.article_comment_edges.append(
                        (comment_node, article_node, {"id": Crawler.relationship_id, "type": "_IN"}))

                    Crawler.relationship_id += 1
                    self.author_comment_edges.append(
                        (author_node, comment_node, {"id": Crawler.relationship_id, "type": "WROTE"}))

                    self.nodes.append((author_node, author_node))
                    self.nodes.append((comment_node, comment_node))

                    self.author_nodes.append(author_node)
                    self.comment_nodes.append(comment_node)
                    # diGraph.add_nodes_from(
                    #     [(comment_node, comment_node)])
                    Crawler.relationship_id += 1

            except Exception as pe:
                print(pe)

        # populate sentiment/comment  and comment/comment edge list
        for p_comment, *_ in self.article_comment_edges:
            self.sentiment_comment_edges.append((p_comment, sentiment[p_comment['sentiment']],
                                                 {"id": Crawler.relationship_id, "type": "_IS",
                                                  "score": p_comment['sentiment_score']}))

            Crawler.relationship_id += 1
            for c_comment, *_ in self.article_comment_edges:
                if c_comment['parent_id'] == p_comment['id']:
                    # nx does not support numpy float
                    c_comment.similarity = round(
                        float(cosine_sim(p_comment['body'], c_comment['body'])), 4)
                    self.comment_comment_edges.append((c_comment, p_comment, {
                        "id": Crawler.relationship_id, "type": "REPLY_TO", "similarity": c_comment['similarity']}))
                    Crawler.relationship_id += 1

    def writeGraphML(self, filename="reddit_graph.graphml"):
        import networkx as nx
        graph = nx.Graph()
        # Add all nodes to the graph
        graph.add_nodes_from(self._packForGraphML(self.article_nodes))
        graph.add_nodes_from(self._packForGraphML(self.author_nodes))
        graph.add_nodes_from(self._packForGraphML(self.sentiment_nodes))

        # Add all edges to the graph
        graph.add_edges_from(self.comment_comment_edges)
        graph.add_edges_from(self.article_comment_edges)
        graph.add_edges_from(self.author_comment_edges)
        graph.add_edges_from(self.sentiment_comment_edges)

        nx.write_graphml(graph, filename)

    def _packForGraphML(self, nodes):
        return [(node, dict(node)) for node in nodes]

    def load_graph(self, filepath, type=Node):
        """
            loads graph from a .graphml file

            @param filepath
                :type string
                :description: filepath

            @param type
                :type class
                :description: class that specify the node type

            :rtype Graph
        """
        return read_graphml(filepath, node_type=type)
