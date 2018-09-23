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
    """
        this class is used to calculate comment features
    """

    def __init__(self, comment):
        self._body = comment.body
        self._length = None
        self.quoted_text_per_length = None
        self._average_word_length = None
        self._reading_level = None

    @property
    def length(self):
        if self._length == None:
            self._length = len(self._body)
        return self._length

    @property
    def quotedTextPerLength(self):
        stack = list()
        count = 0
        startCounting = False
        if self.quoted_text_per_length == None:
            for c in self._body:
                if(startCounting):
                    count += 1

                if c == '\"':
                    stack.append(c)
                    startCounting = True

                if(len(stack) == 2):
                    startCounting = False
                    del stack[:]

        self.quoted_text_per_length = round(count/self._length, 4)

        return self.quoted_text_per_length

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

        return round(self._average_word_length, 3)

    @property
    def readingLevel(self):
        if self._reading_level == None:
            from textstat.textstat import textstat
            self._reading_level = textstat.flesch_kincaid_grade(self._body)

        return self._reading_level


class ID:
    """
        class use to generate Ids for the comment
        to reduce text density on the graph
    """
    id = -1
    id_alpha = 97
    limit = 1000000

    @classmethod
    def getId(cls):

        if cls.id is int and cls.id >= cls.limit:
            cls.id = str(cls.id) + chr(cls.id_alpha)
            cls.id += 1

        if cls.id is str:
            cls.id += chr(cls.id_alpha)
            cls.id_alpha

        cls.id += 1
        return str(cls.id)


class Node:
    """
        base class for all nodes
    """

    def __init__(self, name):
        self.name = name
        self.id_0 = ""

    def __repr__(self):
        if self.id_0:
            return self.id_0

        self.id_0 = str(ID.getId())
        return self.id_0

    def __len__(self):
        return len(self.__dict__)


class AuthorNode(Node, metaclass=MetaNode, Type="a"):
    """
        base class for all nodes
    """

    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return self.name


class CommentNode(Node, metaclass=MetaNode, Type="c"):
    """
        base class for all nodes
    """

    def __init__(self, comment, meta):
        super().__init__("")
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
        super().__repr__()
        return self.Type + self.id_0


class SentimentNode(Node, metaclass=MetaNode, Type="s"):
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return self.name


class ArticleNode(Node, metaclass=MetaNode, Type="ar"):
    """
        base class for all nodes
    """

    def __init__(self, submission):
        super().__init__("")
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count if submission.view_count != None else 0
        # self.upvote_ratio = submission.upvote_ratio
        # self.ups = submission.ups
        # self.downs = submission.downs

    def __repr__(self):
        super().__repr__()
        return self.Type + self.id_0


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

        self._main_graph = None
        self._comment_graph = None

    @property
    def main_graph(self):
        if self._main_graph == None:
            raise Exception("You have to call getGrahp(...) first")

        return self.main_graph

    @property
    def comment_graph(self):
        if self._main_graph == None:
            raise Exception("You have to call getGrahp(...) first")

        return self._comment_graph

    @main_graph.setter
    def main_graph_setter(self,value):
        self._main_graph = value

    @comment_graph.setter
    def comment_graph_setter(self,value):
        self._comment_graph = value
        

    def stream(self, subreddit):
        """
            streams comments from the given subreddit 
        """
        stream = self.reddit.subreddit(subreddit).stream
        for c in stream.submissions():
            graph = self.getGraph(c.id)
            print(nx.clustering(graph))

    
    def getGraph(self, *ids):
        """"
            builds graph from article with submission id
        """
        sentiment = {"Positive": SentimentNode("Positive"), "Negative": SentimentNode(
            "Negative"), "Neutral": SentimentNode("Neutral")}
        ac_edges = []  # article/comment edge
        cc_edges = []  # undirected comment/comment edges
        sc_edges = []  # sentiment/comment edges
        nodes = []
        # create a digraph for comment/comment edges
        diGraph = nx.DiGraph()

        for id in ids:
            try:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)
                article_node = ArticleNode(submission)

                # populate article/comment edge list
                for comment in submission.comments.list():
                    ac_edges.append((
                        article_node, CommentNode(
                            comment, CommentMetaAnalysis(comment)), {"type":"article-comment"}
                    ))
            except Exception as pe:
                print(pe)

        # populate sentiment/comment  and comment/comment edge list
        for _, comment, *_ in ac_edges:
            sc_edges.append((comment, sentiment[comment.sentiment], {
                            "score": comment.sentiment_score,"type":"sentiment-comment"}))
            
            for _, c ,*_ in ac_edges:
                if c.parent_id == comment.id:
                    cc_edges.append((comment, c,  {"type":"parent-child"}))

       # directed graph for comments
        diGraph.add_edges_from(cc_edges) 
        diGraph.add_edges_from(ac_edges)

        # creat a graph for all other edges
        graph = nx.Graph()
        graph.add_edges_from(cc_edges)
        graph.add_edges_from(ac_edges)
        graph.add_edges_from(sc_edges)

        author_comments_edges = []
        for _, comment, *_ in ac_edges:
            author_comments_edges.append((AuthorNode(comment.author), comment, {"type":"author-comment"}))

        diGraph.add_edges_from(author_comments_edges)
        graph.add_edges_from(author_comments_edges)
        # add nodes and node attributes
        for a, *c in ac_edges:
            nodes.append((a, a.__dict__))

        for pc, cc, *_ in cc_edges:
            nodes.append((pc, pc.__dict__))
            nodes.append((cc, cc.__dict__))

        for _, v in sentiment.items():
            nodes.append((v, v.__dict__))

        graph.add_nodes_from(nodes)
        graph.add_nodes_from(diGraph)

        self._comment_graph  = diGraph
        self._main_graph = graph
        
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
    nx.write_graphml(bot.comment_graph,"comment_graph.graphml")

    # nx.draw(graph, with_labels=False, font_weight='bold')
    # plt.show()
    # bot.dump_submission_comments(submission_id, filename)
