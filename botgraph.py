from bot import SentimentAnalysis, RedditBot
import praw
import networkx as nx

class MetaNode(type):
    """
        a metaclass for specifying the node type
    """

    def __init__(metaclass, name, bases, namespace, **kwargs):
        type.__init__(metaclass, name, bases, namespace)

    def __new__(metaclass, name, bases, namespace, **kwargs):
        for k, v in kwargs.items():
            namespace.setdefault(k, v)
        return type.__new__(metaclass, name, bases, namespace)


class Node:
    """
        base class for all nodes
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class AuthorNode(Node, metaclass=MetaNode, Type="Author"):
    """
        base class for all nodes
    """

    def __init__(self, name):
        super().__init__(name)


class CommentNode(metaclass=MetaNode, Type="Comment"):
    """
        base class for all nodes
    """

    def __init__(self, comment):
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.score = comment.score
        self.timestamp = comment.created
        self.id = comment.id
        self.body = comment.body
        self.sentiment_score = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentiment_score)

    def __repr__(self):
        return self.id


class ArticleNode(metaclass=MetaNode, Type="Article"):
    """
        base class for all nodes
    """

    def __init__(self, submission):
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count
        self.upvote_ratio = submission.upvote_ratio
        self.ups = submission.ups
        self.downs = submission.downs

    def __repr__(self):
        return self.id


class Edge:
    """
        base class for relationship between nodes
    """

    def __init__(self, src, dest):
        self._src = src
        self._dest = dest

    @property
    def src(self):
        return self._src

    @property
    def dest(self):
        return self._dest

    def __repr__(self):
        return self._src + "->" + self._dest


class Digraph:
    """
        Directed graph abstraction
    """

    def __init__(self):
        self._edges = {}

    def addNode(self, node):
        if node not in self._edges:
            self._edges[node] = []

    def addEdge(self, edge):
        src = edge.src
        dest = edge.dest

        if src in self._edges:
            self._edges[src].append(dest)
        else:
            self._edges[src] = [dest]

    def childrenOf(self, node):
        return self._edges[node]

    def hasNode(self, node):
        return node in self._edges

    def getNode(self, name):
        for n in self._edges:
            if n.name == name:
                return n
        raise NameError(name)


class Graph(Digraph):
    """
        subclass of Digraph
    """



    def addEdge(self, edge):
        Digraph.addEdge(self, edge)
        rev = Edge(edge.dest, edge.src)
        Digraph.addEdge(self, rev)

class GraphBot(RedditBot):
    """
        builds graph
    """
    def __init__(self, subreddit,username="Cleverchuk", password="BwO9pJdzGaVj2pyhZ4kJ"):
        self.client_secret = "dcnGfpdIFWH-Zk4Vr6mCypz1dmI"
        self.client_id = "n-EWVSgG6cMnRQ"
        self.user_agent = "python:evolutionconvo:v1.0.0 (by /u/%s)" % username
        
        self.reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, 
                                password=password, user_agent=self.user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def getGraph(self, submission_id):
        graph = nx.Graph()
        submission = self.get_submission(submission_id)
        submission.comments.replace_more(limit=None)

        article_node = ArticleNode(submission)

        ac_edges = [(article_node, CommentNode(comment)) for comment in submission.comments.list()]
        authors = set([AuthorNode(comment.author) for a,comment in ac_edges]) # remove dups
        authc_edges = []
        
        for author in authors:
            for a, comment in ac_edges:
                if author.name == comment.author:
                    authc_edges.append((author,comment))
        
        graph.add_edges_from(ac_edges)
        graph.add_edges_from(authc_edges)

        return graph 


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    subreddit = "compsci"
    submission_id = "9bdwe3"
    bot = GraphBot(subreddit)
    graph = bot.getGraph(submission_id)
    
    # plt.subplot(121)
    nx.draw(graph,with_labels=True, font_weight='bold')
    plt.show()
    # bot.dump_submission_comments(submission_id, filename)