from collections import namedtuple
from json import dump as j_dump
from json import dumps
from json import JSONEncoder
from py2neo import (Graph, Node, Relationship)

class DatabaseLayer:
    """
        This class provides a common interface for queries that will performed on a
        database server
    """
    def all(self):
        raise NotImplementedError
    
    def nodes(self):
        raise NotImplementedError

    def relationships(self):
        raise NotImplementedError
    
    def get_relationship_by_type(self, type):        
        raise NotImplementedError
        
    def get_nodes_by_type(self, type):        
        raise NotImplementedError

    def get_nodes_with_field(self, field):   
        raise NotImplementedError
    
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

    def run(self, query):   
        raise NotImplementedError



class Neo4jLayer(DatabaseLayer):
    """
        This class provides the abstraction for Neo4j database using py2neo Graph object
    """
    def __init__(self, graph = Graph("http://localhost:11002/", username="neo4j", password="chubi93")):
        self.graph = graph

    def all(self):
        data =  list(self.graph.run("MATCH (n1)-[r]->(n2) RETURN r").data())
        return [rels["r"] for rels in data]

    def nodes(self):
        pass

    def relationships(self):
        pass

    def get_relationship_by_type(self, type):        
        pass
        
    def get_nodes_by_type(self, type):        
        pass

    def get_nodes_with_field(self, field):   
        pass
    
    def insert_node(self, node):   
        pass

    def insert_relationship(self, relationship):   
        pass

    def merge_node(self, *nodes):   
        pass

    def merge_relationship(self, *relationships):   
        pass

    def delete_node(self, *nodes):   
        pass

    def delete_relationship(self, *relationships):   
        pass

    def drop(self):   
        pass

    def run(self, query):   
        pass


class Query:
    """
        This class performs database queries without knowing the underlying construction
        of the queries. It uses DatabaseLayer object to achieve this
    """
    def __init__(self, db_layer):
        self.db_layer = db_layer

    def all(self):
        return self.db_layer.all()
    
    def nodes(self):
        return self.db_layer.nodes()

    def relationships(self):
        return self.db_layer.relationships()

    def get_relationship_by_type(self, type):        
        return self.db_layer.get_relationship_by_type(type)
        
    def get_nodes_by_type(self, type):        
        return self.db_layer.get_nodes_by_type(type)

    def get_nodes_with_field(self, field):   
        return self.db_layer.get_nodes_with_field(field)

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
