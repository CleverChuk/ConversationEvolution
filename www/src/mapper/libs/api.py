from collections import namedtuple
from json import dump as j_dump
from json import dumps
from json import JSONEncoder
from py2neo import (Graph, Node, Relationship)
"""
def get_nodes_in_article(self, id):
        data = list(self.graph.run("MATCH (n1)-[r]->(n2) WHERE n1.article_id = \'{0}\' RETURN r".format(id)).data())
        return [node["r"] for node in data]
"""


class DatabaseLayer:
    """
        This class provides a common interface for queries that will performed on a
        database server
    """
    # Read api

    def all(self):
        raise NotImplementedError

    def nodes(self):
        raise NotImplementedError

    def get_relationship(self, type):
        raise NotImplementedError

    def get_nodes_by_label(self, type):
        raise NotImplementedError

    def get_equal_str(self, field, value):
        raise NotImplementedError

    def get_equal(self, field, value):
        raise NotImplementedError

    def get_greater(self, field, value):
        raise NotImplementedError

    def get_less(self, field, value):
        raise NotImplementedError

    def get_greater_or_equal(self, field, value):
        raise NotImplementedError

    def get_less_or_equal(self, field, value):
        raise NotImplementedError

    def get_nodes_in_article(self, id):
        raise NotImplementedError

    # Write api
    def insert_node(self, node):
        raise NotImplementedError

    def insert_relationship(self, relationship):
        raise NotImplementedError

    def merge_node(self, *nodes):
        raise NotImplementedError

    def merge_relationship(self, *relationships):
        raise NotImplementedError

    def delete_node(self, *nodes):
        raise NotImplementedError

    def delete_relationship(self, *relationships):
        raise NotImplementedError

    def drop(self):
        raise NotImplementedError

    # User defined api
    def run(self, query):
        raise NotImplementedError


class Neo4jLayer(DatabaseLayer):
    """
        This class provides the abstraction for Neo4j database using py2neo Graph object
    """

    def __init__(self, graph=Graph("http://localhost:11002/", username="neo4j", password="chubi93")):
        self.graph = graph

    def all(self):
        data = list(self.graph.run("MATCH (n1)-[r]->(n2) RETURN r").data())
        return [rels["r"] for rels in data]

    def nodes(self):
        data = list(self.graph.run("MATCH (n) RETURN n").data())
        return [node["n"] for node in data]

    def get_relationship_by_type(self, type):
        data = list(self.graph.run(
            "MATCH (n1)-[r:{0}]->(n2) RETURN r".format(type.upper())).data())
        return [rels["r"] for rels in data]

    def get_nodes_by_label(self, label):
        data = list(self.graph.run(
            "MATCH (n:{0}) RETURN n".format(label)).data())
        return [node["n"] for node in data]

    def get_equal_str(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} = \'{1}\' OR n2.{0} = \'{1}\' RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_equal(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} = {1} OR n2.{0} = {1} RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_greater(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} > {1} OR n2.{0} > {1} RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_greater_or_equal(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} >= {1} OR n2.{0} >= {1} RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_less(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} < {1} OR n2.{0} < {1} RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_less_or_equal(self, field, value):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} <= {1} OR n2.{0} <= {1} RETURN r".format(field, value)).data())
        return [node["r"] for node in data]

    def get_nodes_in_article(self, id):
        data = list(self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.article_id = \'{0}\' AND n1.type =\'comment\' AND n2.type = \'comment\' RETURN r".format(id)).data())
        return [node["r"] for node in data]


class Query:
    """
        This class performs database queries without knowing the underlying construction
        of the queries. It uses DatabaseLayer object to achieve this
    """

    def __init__(self, db_layer):
        if not issubclass(db_layer.__class__, DatabaseLayer):
            raise TypeError(
                "{0} must be a subclass of DatabaseLayer".format(db_layer.__class__))

        self.db_layer = db_layer

    def all(self):
        return self.db_layer.all()

    def nodes(self):
        return self.db_layer.nodes()

    def relationships(self):
        return self.db_layer.relationships()

    def get_relationship_by_type(self, type):
        return self.db_layer.get_relationship_by_type(type)

    def get_nodes_by_label(self, type):
        return self.db_layer.get_nodes_by_label(type)

    def get_equal(self, field, value):
        return self.db_layer.get_equal(field, value)

    def get_equal_str(self, field, value):
        return self.db_layer.get_equal_str(field, value)

    def get_greater(self, field, value):
        return self.db_layer.get_greater(field, value)

    def get_less(self, field, value):
        return self.db_layer.get_less(field, value)

    def get_greater_or_equal(self, field, value):
        return self.db_layer.get_greater_or_equal(field, value)

    def get_less_or_equal(self, field, value):
        return self.db_layer.get_less_or_equal(field, value)

    def get_nodes_in_article(self, id):
        return self.db_layer.get_nodes_in_article(id)

    # Write
    def insert_node(self, node):
        return self.db_layer.insert_relationship(node)

    def insert_relationship(self, relationship):
        return self.db_layer.insert_relationship(relationship)

    def merge_node(self, *nodes):
        return self.db_layer.merge_node(*nodes)

    def merge_relationship(self, *relationships):
        return self.db_layer.merge_relationship(*relationships)

    def delete_node(self, *nodes):
        return self.db_layer.delete_node(*nodes)

    def delete_relationship(self, *relationships):
        return self.db_layer.delete_relationship(*relationships)

    def drop(self):
        return self.db_layer.drop()

    def run(self, query):
        return self.db_layer.run()


class D3helper:
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def transform(cls, *edges):
        """
            this function is used to create data structure that will be
            serialized to JSON for visualization

            @param edges
                :type list
                :description list of Relationship object
        """
        # dictionary to store index
        d = {}
        # list to store nodes
        nodes = []
        # list to store the link namedtuples
        links = []

        # transforms the edges into a data format D3 will use
        for rel in edges:
            n1 = rel.start_node
            n2 = rel.end_node

            # Coerce py2neo to get all the node properties
            n1['name']
            n2['name']
            if n1['id'] not in d:
                nodes.append(n1)
                d[n1['id']] = len(nodes) - 1

            if n2['id'] not in d:
                nodes.append(n2)
                d[n2['id']] = len(nodes) - 1

            # create a simple record type for links
            links.append({"source": d[n1['id']], "target": d[n2['id']]})

        d = {"nodes": nodes, "links": links}

        return d

    @classmethod
    def dumpJSON(cls, filename, data):
        with open(filename, "w") as fp:
            j_dump(data, fp, separators=(',', ':'),
                   cls=CustomJSONEncoder, sort_keys=False, indent=4)

    @classmethod
    def dumpsJSON(cls, data):
        return dumps(data, separators=(',', ':'),
                     cls=CustomJSONEncoder, sort_keys=False, indent=4)


class CustomJSONEncoder(JSONEncoder):
    def default(self, node):
        if isinstance(node, Node):
            return dict(node)
        else:
            return JSONEncoder.default(self, node)
