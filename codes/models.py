
from analyzers import  SentimentAnalysis
from json import JSONEncoder
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
class CustomeEncoder(JSONEncoder):
    """
        Custom encoder for comment class
    """

    def default(self, o):
        return o.__dict__

    def decode_object(self, o):
        pass


class Submission:
    """
        submission object
    """

    def __init__(self, submission):
        self.author_fullname = submission.author_fullname
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count
        self.upvote_ratio = submission.upvote_ratio
        self.ups = submission.ups
        self.downs = submission.downs
        self.comments = [Comment(comment) for comment in submission.comments]


class Comment:
    """
        comment object
    """

    def __init__(self, comment):
        from analyzers import CommentMetaAnalysis
        metaAnalysis = CommentMetaAnalysis(comment)
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.parent_id = comment.parent().id
        self.score = comment.score
        self.timestamp = comment.created
        self.id = comment.id
        self.body = comment.body
        self.length = metaAnalysis.length
        self.averageWordLength = metaAnalysis.averageWordLength
        self.quotedTextPerLength = metaAnalysis.quotedTextPerLength
        self.readingLevel = metaAnalysis.readingLevel
        self.sentiment_score = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentiment_score)
        self.replies = [Comment(c) for c in comment.replies]



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


class ID:
    """
        class use to generate Ids for the comment
        to reduce text density on the graph
    """
    id = -1
    id_alpha = 97
    limit = 1000000
    hit_limit = False

    @classmethod
    def getId(cls):
        id = None

        if cls.id >= cls.limit or cls.hit_limit:
            cls.hit_limit = True

            if cls.id == cls.limit:
                cls.id = 0

            if cls.id_alpha > 122:
                cls.id += 1
                cls.id_alpha = 97

            id = chr(cls.id_alpha) + str(cls.id)
            cls.id_alpha += 1

        else:
            cls.id += 1
            id = cls.id

        return str(id)


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
        Author node
    """

    def __init__(self, author):
        # self.account_created = author.created_utc

        super().__init__(author)

    def __repr__(self):
        return self.name


class CommentNode(Node, metaclass=MetaNode, Type="c"):
    """
        comment nodes
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
        self.similarity = 1.0

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
        Article node
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



