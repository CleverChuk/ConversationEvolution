# Author: Chukwubuikem Ume-Ugwa
# Purpose: Record models use to create graph nodes

from analyzers import  SentimentAnalysis
"""
@param 
    :type
    :description:
            
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
ANONYMOUS_USER = "Anonymous"
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
    count = 0
    def __init__(self, author):
        # help neo4j distinguish anonymous authors          
        if(author == ANONYMOUS_USER):
            author += str(AuthorNode.count)
            AuthorNode.count += 1

        self.id = author 
        self.name = author      
        super().__init__("author")

    def __repr__(self):        
        return self.id

class CommentNode(Node):
    """
        comment nodes
    """
    def __init__(self, aId, comment, meta):        
        self.id = comment.id
        self.article_id = aId
        self.parent_id = comment.parent().id
        self.author = ANONYMOUS_USER if comment.author == None else comment.author.name
        self.score = comment.score
        self.timestamp = int(comment.created)
        self.body = comment.body
        self.length = meta.length
        self.average_word_length = meta.average_word_length
        self.quoted_text_per_length = meta.quoted_text_per_length
        self.reading_level = meta.reading_level
        self.sentimentScore = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentimentScore)
        self.similarity = 1.0        
        super().__init__("comment")

class SentimentNode(Node):
    def __init__(self, value):        
        self.id = value   
        self.name = value
        super().__init__("sentiment")     

    def __repr__(self):
        return self.id

class ArticleNode(Node):
    """
        Article node
    """
    def __init__(self, submission):
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count if submission.view_count != None else 0
        self.timestamp = int(submission.created_utc)
        self.isVideo = submission.is_video
        self.upvote_ratio = submission.upvote_ratio
        super().__init__("article")
