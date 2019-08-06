from django.db import models


# Create your models here.


class Node(dict):
    """
        base class for all nodes
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        self['radius'] = 2.8

    def __getitem__(self, key):
        val = dict.get(self, key, None)
        return val

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __hash__(self):
        return hash(self["id"])
    
    def __str__(self):
        return "{0}".format(self['type'])


class TreeNode(Node):
    def __init__(self, id, type="article", *args, **kwargs):
        super(TreeNode, self).__init__(*args, **kwargs)
        self["id"] = id
        self["type"] = type
        self["children"] = []

    def add_child(self, child):
        self["children"].append(child)

    
        
        