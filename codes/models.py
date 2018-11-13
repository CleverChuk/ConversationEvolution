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
class CustomEncoder(JSONEncoder):
    """
        Custom encoder for comment class
    """
    def default(self, o):
        return o.__dict__

    def decode_object(self, o):
        pass


class Submission:
    """
        submission object use to write to json
    """
    def __init__(self, submission):
        self.author_fullname = submission.author_fullname if hasattr(submission,"author_fullname") else "Anonymous"
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count
        self.upvote_ratio = submission.upvote_ratio
        self.ups = submission.ups
        self.downs = submission.downs
        self.comments = [Comment(comment) for comment in submission.comments]
    
    def __repr__(self):
        return self.title


class Comment:
    """
        comment object used to write to json
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
        self.sentimentScore = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentimentScore)
        self.replies = [Comment(c) for c in comment.replies]

    def __repr__(self):
        return self.body

class DecodeSubmission:
    def __init__(self,obj):
        self.author_fullname = obj["author_fullname"]
        self.id = obj["id"]
        self.title = obj["title"]
        self.view_count = obj["view_count"]
        self.upvote_ratio = obj["upvote_ratio"]
        self.ups = obj["ups"]
        self.downs = obj["downs"]
        self.comments = [DecodeComment(comment) for comment in obj["comments"]]

    def __repr__(self):
        return self.title

class DecodeComment:
    def __init__(self, obj):
        self.author =  obj["author"]
        self.parent_id = obj["parent_id"]
        self.score =  obj["score"]
        self.timestamp =  obj["timestamp"]
        self.id =  obj["id"]
        self.body =  obj["body"]
        self.length =  obj["length"]
        self.averageWordLength =  obj["averageWordLength"]
        self.quotedTextPerLength =  obj["quotedTextPerLength"]
        self.readingLevel =  obj["readingLevel"]
        self.sentimentScore =  obj["sentimentScore"]
        self.sentiment =  obj["sentiment"]
        self.replies = [DecodeComment(c) for c in  obj["replies"]]

    def __repr__(self):
        return self.body

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
    def __init__(self, _type):
        self.type = _type
        self.id_0 = ""

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        if self.id_0:
            return "{0}".format(self.id_0)

        self.id_0 = ID.getId()
        return "{0}".format(self.id_0)

    def __repr__(self):
        if self.id_0:
            return "{0}".format(self.id_0)

        self.id_0 = ID.getId()
        return "{0}".format(self.id_0)


class AuthorNode(Node):
    """
        Author node
    """
    def __init__(self, author):
        # self.account_created = author.created_utc
        super().__init__("author")
        self.name = author

    def __repr__(self):
        return self.name


class CommentNode(Node):
    """
        comment nodes
    """
    def __init__(self, aId, comment, meta):
        super().__init__("comment")
        self.article_id = aId
        self.parent_id = comment.parent().id
        self.id = comment.id
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.score = comment.score
        self.timestamp = int(comment.created)
        self.body = comment.body
        self.length = meta.length
        self.averageWordLength = meta.averageWordLength
        self.quotedTextPerLength = meta.quotedTextPerLength
        self.readingLevel = meta.readingLevel
        self.sentimentScore = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentimentScore)
        self.similarity = 1.0


class SentimentNode(Node):
    def __init__(self, value):
        super().__init__("sentiment")
        self.value = value

    def __repr__(self):
        return self.value


class ArticleNode(Node):
    """
        Article node
    """
    def __init__(self, submission):
        super().__init__("article")
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count if submission.view_count != None else 0
        self.timestamp = submission.created_utc
        self.isVideo = submission.is_video
        self.upvote_ratio = submission.upvote_ratio