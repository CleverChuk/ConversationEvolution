from bot import SentimentAnalysis, RedditBot
import praw
from nltk.tokenize import TweetTokenizer
import networkx as nx
from gensim import corpora
from string import punctuation

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


class Doc2Vec(corpora.Dictionary):
    """
        a subclass of Dictonary to generate document corpus vector
    """

    def __init__(self, reference_doc):
        self._ref = reference_doc
        # self._copra = {} # dictionary to hold generated copra; key: comment_id, value: corpus
        self.__process_ref_doc()
        super().__init__(self._ref)

    def __process_ref_doc(self):
        self._ref = self._ref.split("\n")  # splits at new lines
        self._ref = [[word for word in line.split() if len(word) > 3]  # get only words greater than 3 letters
                     for line in self._ref if len(line) > 3]  # get only lines with more than 3 words
        temp = []
        self._ref = [temp + doc for doc in self._ref]

    def getCorpus(self, doc):
        if isinstance(doc, list):
            return super().doc2bow(doc)

        doc = doc.split()
        return super().doc2bow(doc)


class CommentMetaAnalysis:
    """
        this class is used to calculate comment features
    """

    def __init__(self, comment):
        self._body = comment.body
        self._length = None
        self._quoted_text_per_length = None
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
        if self._quoted_text_per_length == None:
            for c in self._body:
                if(startCounting):
                    count += 1

                if c == '\"':
                    stack.append(c)
                    startCounting = True

                if(len(stack) == 2):
                    startCounting = False
                    del stack[:]

            self._quoted_text_per_length = round(count/self._length, 4)

        return self._quoted_text_per_length

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

    def __init__(self, author):
        # self.account_created = author.created_utc

        super().__init__(author)

    def __repr__(self):
        return self.name


class CommentNode(Node, metaclass=MetaNode, Type="c"):
    """
        base class for commemnt nodes
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
        self.corpus = None

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
        self.timestamp = submission.created_utc
        self.edited = submission.edited
        self.is_video = submission.is_video
        self.upvote_ratio = submission.upvote_ratio
        # self.over18 = submission.over18

    def __repr__(self):
        super().__repr__()
        return self.Type + self.id_0


class GraphBot(RedditBot):
    """
        builds graph
    """

    def __init__(self, subreddit, username="CleverChuk", password="BwO9pJdzGaVj2pyhZ4kJ"):
        self._ids = None
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
    def main_graph_setter(self, value):
        self._main_graph = value

    @comment_graph.setter
    def comment_graph_setter(self, value):
        self._comment_graph = value

    def stream(self, subreddit):
        """
            streams graphs from the given subreddit 
        """
        stream = self.reddit.subreddit(subreddit).stream
        for c in stream.submissions():
            yield self.getGraph(c.id)

    def commentGraph(self):
        """
            load a subgraph of comment to comment
        """
        pass

    def articleGraph(self):
        """"
            load a subgraph of article to comment
        """
        pass

    def sentimentGraph(self):
        """
            load a subgraph of sentiment to comment
        """
        pass

    def getGraph(self, *ids):
        """"
            builds graph from article with submission id
        """
        self._ids = ids  # save the ids for future queries
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
                            comment, CommentMetaAnalysis(comment)),
                        {"type": "article-comment"}
                    ))
            except Exception as pe:
                print(pe)

        # populate sentiment/comment  and comment/comment edge list
        for _, comment, *_ in ac_edges:
            sc_edges.append((comment, sentiment[comment.sentiment], {
                            "score": comment.sentiment_score, "type": "sentiment-comment"}))
            doc2vec = Doc2Vec(comment.body)
            comment.corpus = str(doc2vec.getCorpus(comment.body))
            for _, c, *_ in ac_edges:
                if c.parent_id == comment.id:
                    c.corpus = str(doc2vec.getCorpus(c.body))
                    cc_edges.append((comment, c,  {"type": "parent-child"}))

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
            author_comments_edges.append(
                (AuthorNode(comment.author), comment, {"type": "author-comment"}))

        # add nodes and node attributes
        for a, *c in ac_edges:
            nodes.append((a, a.__dict__))

        for pc, cc, *_ in cc_edges:
            nodes.append((pc, pc.__dict__))
            nodes.append((cc, cc.__dict__))

        for _, v in sentiment.items():
            nodes.append((v, v.__dict__))

        diGraph.add_edges_from(author_comments_edges)
        graph.add_nodes_from(diGraph)
        graph.add_nodes_from(nodes)

        self._comment_graph = diGraph
        self._main_graph = graph

        return graph


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # "9bdwe3","9f3vyq","9f4lcs"
    subreddit = "compsci"
    filename = "../raw/data.json"
    # username = input("Enter username:")
    # password = input("Enter password(Not hidden, so make sure no one is looking):")

    bot = GraphBot(subreddit)
    ids = bot.get_submissions()
    graph = bot.getGraph(*ids)
    nx.write_graphml(graph, "reddit_graph.graphml")
    nx.write_graphml(bot.comment_graph, "comment_graph.graphml")
    # for g in bot.stream(subreddit):
    #     print(nx.clustering(g))
    # nx.draw(graph, with_labels=False, font_weight='bold')
    # plt.show()
    # bot.dump_submission_comments(submission_id, filename)
