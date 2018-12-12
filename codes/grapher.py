# Author: Chukwubuikem Ume-Ugwa
# Purpose: Class use to generate a graph from pulled data
from networkx import (Graph, DiGraph, read_graphml)
from analyzers import CommentAnalysis
from textsim import cosine_sim
from models import CommentNode, AuthorNode, Node, ArticleNode, SentimentNode
from base import RedditBot
from mapper_functions import cluster_on_numeric_property


def load_graph(filepath, type):
    """
        loads graph from a .graphml file

        @param subreddit
            :type string
            :description: filepath

        @param subreddit
            :type class
            :description: class that specify the node model

        :rtype Graph
    """
    return read_graphml(filepath, node_type = type)


class GraphBot(RedditBot):
    """
        A subclass of RedditBot that can be used to build mapper graph
    """

    def __init__(self, subreddit, username = "CleverChuk", password = "BwO9pJdzGaVj2pyhZ4kJ" , property_key = "sentiment_score", epsilon = 0.5, intervals = 3, APP_NAME="myapp", VERSION = "1.0.0"):
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
        super().__init__(subreddit, username, password,VERSION=VERSION, APP_NAME=APP_NAME)
        self.property_key = property_key
        self.epsilon = epsilon
        self.intervals = intervals

        self.article_comment_edges = []  # article/comment edge
        self.comment_comment_edges = []  # undirected comment/comment edges
        self.sentiment_comment_edges = []  # sentiment/comment edges
        self.author_comment_edges = []  # author/comment edges

        self.nodes = []
        self.comment_nodes = []
        self.article_nodes = []
        self.sentiment_nodes= []
        self.author_nodes = []

    def isRemoved(self, comment):
        """
            filters a comment from being added to the graph if it has be removed

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
            yield self.getGraph(submission.id)

    def getGraph(self, *ids):
        """"
            builds graph from article with submission id

            @param *ids: 
                :type list
                description: list of submission ids in the subreddit
            
            :rtype Graph
        """
        self.ids = ids  # save the ids for future queries
        sentiment = {"Positive": SentimentNode("Positive"), "Negative": SentimentNode(
            "Negative"), "Neutral": SentimentNode("Neutral")}



        # create a digraph for comment/comment edges
        diGraph = DiGraph()
        # create a graph object
        graph = Graph()

        # add the sentiment nodes to the node list
        for _, v in sentiment.items():
            self.sentiment_nodes.append(v)
            self.nodes.append((v, v.__dict__))

        for id in ids:
            try:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)
                article_node = ArticleNode(submission)

                self.nodes.append((article_node, article_node.__dict__))
                self.article_nodes.append(article_node)

                # populate article/comment edge list
                for comment in submission.comments.list():
                    comment_node = CommentNode(article_node.id, comment, CommentAnalysis(comment))
                    author_node = AuthorNode(comment_node.author)
                    self.article_comment_edges.append((comment_node, article_node, {"type": "_IN"}))

                    self.author_comment_edges.append((author_node, comment_node, {"type": "WROTE"}))
                    self.nodes.append((author_node, author_node.__dict__))
                    self.nodes.append((comment_node, comment_node.__dict__))
                    
                    self.author_nodes.append(author_node)
                    self.comment_nodes.append(comment_node)
                    diGraph.add_nodes_from([(comment_node, comment_node.__dict__)])

                
            except Exception as pe:
                print(pe)

        # populate sentiment/comment  and comment/comment edge list
        for p_comment, *_ in self.article_comment_edges:
            self.sentiment_comment_edges.append((sentiment[p_comment.sentiment], p_comment, 
            {"type": "_IS","score": p_comment.sentiment_score}))

            for c_comment, *_ in self.article_comment_edges:
                if c_comment.parent_id == p_comment.id:
                    # nx does not support numpy float
                    c_comment.similarity = round(float(cosine_sim(p_comment.body, c_comment.body)), 4)
                    self.comment_comment_edges.append((c_comment, p_comment, {"type": "REPLY_TO", "similarity": c_comment.similarity}))

        # add nodes for mapper graph
        _nodes = []
        for cc, pc, *_ in self.comment_comment_edges:
            _nodes.append(cc)
            _nodes.append(pc)

        _nodes = list(set(_nodes)) #remove duplicates

        # build a digraph from data
        diGraph.add_edges_from(self.comment_comment_edges)

        # build an  undirected graph from data
        graph.add_edges_from(self.author_comment_edges)
        graph.add_edges_from(self.comment_comment_edges)
        graph.add_edges_from(self.article_comment_edges)

        graph.add_edges_from(self.sentiment_comment_edges)
        graph.add_nodes_from(self.nodes)

        # full graphs
        self.comment_graph = diGraph
        self.main_graph = graph

        # mapper graph
        self.mapper_graph, self.mapper_edges =  cluster_on_numeric_property(self.comment_comment_edges, self.epsilon,
         property_key = self.property_key, num_interval = self.intervals)
        self.mapper_nodes =  list(self.mapper_graph.nodes())
        
        return graph




