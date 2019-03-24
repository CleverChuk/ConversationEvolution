from django.db import models

# Create your models here.


class Node(dict):
    """
        base class for all nodes
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

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