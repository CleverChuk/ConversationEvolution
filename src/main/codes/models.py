# Author: Chukwubuikem Ume-Ugwa
# Purpose: Record models use to create graph nodes

from analyzers import SentimentAnalyzer

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
ANONYMOUS_USER = "anonymous"


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


class Node(dict):
    """
        base class for all nodes
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        val = dict.get(self, key, "")
        return val

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return "{0}".format(self['type'])


class AuthorNode(Node):
    """
        Author node
    """
    count = 0

    def __init__(self, subreddit, author):
        # help neo4j distinguish anonymous authors
        if(author == ANONYMOUS_USER):
            author += str(AuthorNode.count)
            AuthorNode.count += 1
        d = {
            'id': author,
            'name': author,
            'type': "author",
            'subreddit': subreddit
        }
        super().__init__(d)

    def __repr__(self):
        return self['id']


class CommentNode(Node):
    """
        comment nodes
    """

    def __init__(self, subreddit, aId, comment, meta):
        d = {
            'id': comment.id,
            'article_id': aId,
            'parent_id': comment.parent().id,
            'is_root': comment.parent().id == aId,
            'author': ANONYMOUS_USER if comment.author == None else comment.author.name,
            'score': comment.score,
            'timestamp': int(comment.created),
            'body': comment.body,
            'length': meta.length,
            'average_word_length': meta.average_word_length,
            'quoted_text_per_length': meta.quoted_text_per_length,
            'reading_level': meta.reading_level,
            'sentiment_score': SentimentAnalyzer.get_sentiment(comment),
            'sentiment': SentimentAnalyzer.convert_score(SentimentAnalyzer.get_sentiment(comment)),
            'similarity': 1.0,            
            'type': "comment",
            'subreddit': subreddit

        }
        super().__init__(d)


class SentimentNode(Node):
    def __init__(self, subreddit, value):

        d = {
            'id': value,
            'name': value,
            'type': "sentiment",
            'subreddit': subreddit
        }
        super().__init__(d)


class ArticleNode(Node):
    """
        Article node
    """

    def __init__(self, subreddit, submission):
        d = {'id': submission.id,
             'title': submission.title,
             'view_count': submission.view_count if submission.view_count != None else 0,
             'timestamp': int(submission.created_utc),
             'isVideo': submission.is_video,
             'upvote_ratio': submission.upvote_ratio,
             'type': 'article',
             'subreddit': subreddit
             }
        super().__init__(d)


class Relationship(dict):
    def __init__(self, start_node, end_node, relationship_type="TO", **properties):
        self.start_node = start_node
        self.end_node = end_node
        self.relationship_type = relationship_type
        self.update(properties)

    def __getitem__(self, key):
        return dict.get(self, key)

    def __repr__(self):
        return "{0}<--{1}-->{2}".format(self.start_node, self.relationship_type, self.end_node)
