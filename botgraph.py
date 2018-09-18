from bot import SentimentAnalysis, RedditBot
import praw
from nltk.tokenize import TweetTokenizer
import networkx as nx


"""
On second thought, some of the other argument-related annotators I'm working on
(such as the level of formality, level of charitability, etc.) might be overkill for this first paper.
 Some features that should be relatively easy to implement and add into the graph are:
> Length of the comment
> average word length
> Number of quoted text per comment length:
> Flesch-kincaid reading level (there is a python library called "textstat" that implements this)
> If there is time, it would be interesting to encode how similar two comments are as
a relationship between them, or perhaps annotating each comment with a value representing
how similar it is to the root comment of its thread. The easiest way to do this is by using doc2vec from the genSim library.
"""


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


class CommentMetaAnalysis:
    def __init__(self, comment):
        self._body = comment.body
        self._length = None
        self._count_quoted_text = None
        self._average_word_length = None
        self._reading_level = None

    @property
    def length(self):
        if self._length == None:
            self._length = len(self._body)
        return self._length

    @property
    def quotedTextPerLength(self):
        # incorrect
        stack = list()
        count = 0
        startCounting = False
        if self._count_quoted_text == None:
            for char in self._body:
                if char == '\"':
                    stack.append(char)

                if(startCounting):
                    count +=1

        self._count_quoted_text = len(stack)//2

        return self._count_quoted_text

    @property
    def averageWordLength(self):

        if self._average_word_length == None:
            import string
            from statistics import mean
            from collections import defaultdict

            tokenDict = defaultdict(int)
            tweetTokenizer = TweetTokenizer()
            tokens = tweetTokenizer.tokenize(self._body)

            for token in tokens:
                if token in string.punctuation:
                    continue
                tokenDict[token] += len(token)

            self._average_word_length = mean(tokenDict.values())

        return round(self._average_word_length,3)

    @property
    def readingLevel(self):
        if self._reading_level == None:
            from textstat.textstat import textstat
            self._reading_level = textstat.flesch_kincaid_grade(self._body)

        return self._reading_level


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

    def __init__(self, comment, meta):
        self.parent_id = comment.parent().id
        self.id = comment.id
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.score = comment.score
        self.timestamp = comment.created
        self.body = comment.body
        self.length = meta.length
        self.averageWordLength = meta.averageWordLength
        self.quotedTextPerLength = meta.quotedTextPerLength
        self.readingLevel = meta.readingLevel
        self.sentiment_score = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentiment_score)

    def __repr__(self):
        return self.id


class SentimentNode(Node, metaclass=MetaNode, Type="Sentiment"):
    def __init__(self, value):
        super().__init__(value)


class ArticleNode(metaclass=MetaNode, Type="Article"):
    """
        base class for all nodes
    """

    def __init__(self, submission):
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count if submission.view_count != None else 0
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

    def __init__(self, subreddit, username="CleverChuk", password="BwO9pJdzGaVj2pyhZ4kJ"):
        self.client_secret = "dcnGfpdIFWH-Zk4Vr6mCypz1dmI"
        self.client_id = "n-EWVSgG6cMnRQ"
        self.user_agent = "python:evolutionconvo:v1.0.0 (by /u/%s)" % username

        self.reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret,
                                  password=password, user_agent=self.user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def getGraph(self, *ids):
        """"
            builds graph from article with submission id
        """
        sentiment = {"Positive": SentimentNode("Positive"), "Negative": SentimentNode(
            "Negative"), "Neutral": SentimentNode("Neutral")}
        graph = nx.Graph()
        ac_edges = []  # article/comment edge
        authc_edges = []  # author/comment edges
        cc_edges = []  # comment/comment edges
        sc_edges = []  # sentiment/comment edges
        nodes = []

        for id in ids:
            try:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)
                article_node = ArticleNode(submission)

                # populate article/comment edge list
                for comment in submission.comments.list():
                    ac_edges.append((article_node, CommentNode(
                        comment, CommentMetaAnalysis(comment))))
            except Exception as pe:
                print(pe)

        authors = set([AuthorNode(comment.author)
                       for a, comment in ac_edges])  # remove dups

        # populate sentiment/comment  and comment/comment edge list
        for author, comment in ac_edges:
            sc_edges.append((comment, sentiment[comment.sentiment]))
            for a, c in ac_edges:
                if c.parent_id == comment.id:
                    cc_edges.append((comment, c))

        # populate author/comment edge list
        for author in authors:
            for a, comment in ac_edges:
                if author.name == comment.author:
                    authc_edges.append((author, comment))

        graph.add_edges_from(ac_edges)
        graph.add_edges_from(authc_edges)
        graph.add_edges_from(cc_edges)
        graph.add_edges_from(sc_edges)

        # add nodes and node attributes
        for a, c in ac_edges:
            nodes.append((a, a.__dict__))

        for author, c in authc_edges:
            nodes.append((author, author.__dict__))

        for pc, cc in cc_edges:
            nodes.append((pc, pc.__dict__))
            nodes.append((cc, cc.__dict__))

        for _, v in sentiment.items():
            nodes.append((v, v.__dict__))

        graph.add_nodes_from(nodes)

        return graph


def checkNone(o):
    print(o.__dict__)
    return o.__dict__ is None


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # "9bdwe3","9f3vyq","9f4lcs"
    subreddit = "compsci"
    filename = "data.json"
    # username = input("Enter username:")
    # password = input("Enter password(Not hidden, so make sure no one is looking):")

    bot = GraphBot(subreddit)
    ids = bot.get_submissions()
    graph = bot.getGraph(*ids)
    nx.write_graphml(graph, "reddit_graph.graphml")

    # nx.draw(graph, with_labels=False, font_weight='bold')
    # plt.show()
    # bot.dump_submission_comments(submission_id, filename)
