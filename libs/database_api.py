import os
from json import JSONEncoder
from json import dump as j_dump
from json import dumps

from py2neo import (Graph, Node)

from libs.mapper import TreeMapper

NEO4J_URL = os.environ["NEO4J_URL"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

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

    def get_subreddit_graph(self, subreddit=None):
        raise NotImplementedError

    def get_nodes_in_article(self, id):
        raise NotImplementedError

    def get_all_articles(self):
        raise NotImplementedError

    def get_articles_in_subreddit(self, subreddit):
        raise NotImplementedError

    def get_edges_in_subreddit(self, subreddit):
        raise NotImplementedError

    def get_comments_in_article(self, id):
        raise NotImplementedError

    def get_topological_lens(self):
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

    # User defined query
    def run(self, query):
        raise NotImplementedError


class Neo4jLayer(DatabaseLayer):
    """
        This class provides the abstraction for Neo4j database using py2neo Graph object
    """

    def __init__(self):
        if ":" in NEO4J_URL:
            self.graph = Graph(
                NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
        else:
            self.graph = Graph(
                host=NEO4J_URL, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

    def all(self):
        data = self.graph.run("MATCH (n1)-[r]->(n2) RETURN r").data()
        return [rels["r"] for rels in data]

    def nodes(self):
        data = self.graph.run("MATCH (n) RETURN n").data()
        return [node["n"] for node in data]

    def get_relationship_by_type(self, type):
        data = self.graph.run(
            "MATCH (n1)-[r:{0}]->(n2) RETURN r".format(type.upper())).data()
        return [rels["r"] for rels in data]

    def get_nodes_by_label(self, label):
        data = self.graph.run("MATCH (n:{0}) RETURN n".format(label)).data()
        return [node["n"] for node in data]

    def get_equal_str(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} = \'{1}\' OR n2.{0} = \'{1}\' RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_equal(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} = {1} OR n2.{0} = {1} RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_greater(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} > {1} OR n2.{0} > {1} RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_greater_or_equal(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} >= {1} OR n2.{0} >= {1} RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_less(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} < {1} OR n2.{0} < {1} RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_less_or_equal(self, field, value):
        data = self.graph.run(
            "MATCH (n1)-[r]->(n2) WHERE n1.{0} <= {1} OR n2.{0} <= {1} RETURN r".format(field, value)).data()
        return [node["r"] for node in data]

    def get_nodes_in_article(self, id):
        comment_links = "MATCH (n1)-[r]->(n2) WHERE n1.article_id = \'{0}\' RETURN r".format(
            id)
        author_links = " UNION MATCH (n1:author)-[r:WROTE]->(n2:comment) WHERE n2.article_id = \'{0}\' RETURN r".format(
            id)

        query = comment_links + author_links
        data = self.graph.run(query).data()
        return [node["r"] for node in data]

    def get_all_articles(self):
        query = "MATCH (n) WHERE n.type=\'article\' return n"
        data = self.graph.run(query).data()
        return [node['n'] for node in data]

    def get_articles_in_subreddit(self, subreddit):
        query = "MATCH (n:article) WHERE n.subreddit=\'{0}\' RETURN n".format(
            subreddit)
        data = self.graph.run(query).data()

        return [node["n"] for node in data]

    def get_edges_in_subreddit(self, subreddit):
        query = "MATCH (n0)-[r]->(n1) WHERE n0.subreddit=\'{0}\' OR  n1.subreddit=\'{0}\' RETURN r".format(
            subreddit)
        data = self.graph.run(query).data()

        return [node["r"] for node in data]

    def get_comments_in_article(self, id):
        query = "MATCH (n1:comment)-[r]->(n2:comment) WHERE n1.article_id = \'{0}\' RETURN r".format(
            id)
        data = self.graph.run(query).data()
        return [node["r"] for node in data]

    def get_subreddit_graph(self, subreddit=None):
        data = self.graph.run("MATCH (n1)-[r:_IN_]->(n2) RETURN r").data()
        return [node["r"] for node in data]

    def get_topological_lens(self):

        query = "MATCH(n:comment) return n LIMIT 1"
        node = [dict(node['n']) for node in self.graph.run(query).data()]
        node = node[0]
        options = []

        def format_prop(string):
            tokens = string.split('_')
            return " ".join(tokens).capitalize()

        for prop, val in node.items():
            if type(val) is int or type(val) is float:
                options.append({"value": prop, "label": format_prop(prop)})

        return options


class Query:
    """
        This class performs database queries without knowing the underlying construction
        of the queries. 
        It uses DatabaseLayer object to achieve this
    """

    def __init__(self, db_layer):
        # db_layer must implement DatabaseLayer
        if not issubclass(db_layer.__class__, DatabaseLayer):
            raise TypeError(
                "{0} must be a subclass of DatabaseLayer".format(db_layer.__class__))

        self.db_layer = db_layer

    # read methods
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

    def get_all_articles(self):
        return self.db_layer.get_all_articles()

    def get_articles_in_subreddit(self, subreddit):
        return self.db_layer.get_articles_in_subreddit(subreddit)

    def get_edges_in_subreddit(self, subreddit):
        return self.db_layer.get_edges_in_subreddit(subreddit)

    def get_comments_in_article(self, id):
        return self.db_layer.get_comments_in_article(id)

    def get_subreddit_graph(self, subreddit=None):
        return self.db_layer.get_subreddit_graph(subreddit)

    def get_topological_lens(self):
        return self.db_layer.get_topological_lens()

    # Write methods
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
        return self.db_layer.run(query)


class D3helper:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def graph_transform(*edges):
        """
            this function is used to create data structure that will be
            serialized to JSON for visualization

            @param edges
                :type list
                :description list of Relationship object
        """
        # dictionary to store index
        output = {}
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
            if n1['id'] not in output:
                # add node to list
                nodes.append(n1)
                # add node index to index dictionary
                output[n1['id']] = len(nodes) - 1

            if n2['id'] not in output:
                nodes.append(n2)
                output[n2['id']] = len(nodes) - 1

            # create a simple record type for D3 links using the
            # indices in the index dictionary
            links.append({"source": output[n1['id']], "target": output[n2['id']]})

        # create a dictionary containing D3 formatted nodes and links
        output = {"nodes": nodes, "links": links}

        return output


    @staticmethod
    def tree_transform(root, nodes):
        tree_mapper = TreeMapper()
        return tree_mapper.make_tree(root, nodes)

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
