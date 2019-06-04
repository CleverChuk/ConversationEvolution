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

    def __len__(self):
        return len(self)

    def __str__(self):
        return "{0}".format(self['type'])

from collections import defaultdict
class TreeNode(Node):
    def __init__(self, id, edges=[], found = defaultdict(int)):
        self.found = found
        self["id"] = id
        self["children"] = [
            TreeNode(node["id"], edges, found)
            for node in self.nodes(edges)            
            if node != None and node["parent_id"] == id
        ]

    def nodes(self, edges):        
        for edge in edges:
            start = edge.start_node
            end = edge.end_node
            print(self.found)
            if not self.found[start["id"]]:
                if start["type"] == "comment":
                    self.found[start["id"]] = 1
                    yield start
                    
            if not self.found[end["id"]]:  
                if end["type"] == "comment":
                    self.found[end["id"]] = 1
                    yield end
                