from collections import namedtuple
from json import dump as j_dump
from json import dumps
from json import JSONEncoder
from py2neo import (Graph, Node, Relationship)


class Query:
    def __init__(self, db_url="http://localhost:11002/", username="neo4j", password="chubi93"):
        self.graph = Graph(db_url, username=username, password=password)

    def all(self):
        """
            returns py2neo relationshipMatch object generator
        """
        data =  list(self.graph.run("MATCH (n1)-[r]->(n2) RETURN r").data())
        return [rels["r"] for rels in data]
        


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
                :description list of py2neo Relationship object
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
            n1["name"]
            n2["name"]
           
            
            if n1 not in d:
                nodes.append(n1)
                d[n1] = len(nodes) - 1

            if n2 not in d:
                nodes.append(n2)
                d[n2] = len(nodes) - 1

            # create a simple record type for links
            links.append({"source": d[n1], "target": d[n2]})

        d = {"nodes": nodes, "links": links}

        return d

    @classmethod
    def dumpJSON(cls, filename, data):
        with open(filename, "w") as fp:
            j_dump(data, fp, separators=(',', ':'),
                   cls=CustomJSONEncoder, sort_keys=False, indent=4)

    @classmethod
    def dumpsJSON(cls, data):
        return dumps(data,separators=(',', ':'),
                   cls=CustomJSONEncoder, sort_keys=False, indent=4)


class CustomJSONEncoder(JSONEncoder):
    def default(self, node):
        if isinstance(node, Node):
            return dict(node)
        else:
            return JSONEncoder.default(self,node)
