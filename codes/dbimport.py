from py2neo import (Graph, Node, Relationship)
import csv
from models import (CommentNode)


class Loader:    
    """
        Class used to import Nodes and edges into an existing database.
    """

    def __init__(self, url="http://localhost:11002/", username="neo4j", password="chubi93"):
        """
            @param url
                :type String
                :description: database url
            
            @param username
                :type String
                :description: database username

            @param password
                :type String
                :description: database login password
        """
        self.node_dict = {}
        self.rels = []
        self.__start = ":START_ID"
        self.__end = ":END_ID"
        self.__type = ":TYPE"
        self.__key = "id"

        self.label = None
        self.graph = Graph(url, username = username, password = password)

    def write_nodes_from_list(self, nodes, label = "`Node`", primary_key = None):
        """
            helper method for loading nodes from list into db. 
            Assumes all nodes has "id" attribute if primary_key is 
            not provided
        """
        self.load_nodes_from_list(nodes,label)
        for node in self.node_dict.values():
            self.graph.merge(node, label, self.__key if primary_key == None else primary_key)

    def write_edges_from_list(self, edges, type = "TO", primary_key = None):
        """
            helper method for loading edges from list into db. 
            Assumes all edges has "id" attribute if primary_key is 
            not provided
        """
        for rel in self.load_edges_from_list(edges, type):
            self.graph.merge(rel,type, self.__key if primary_key == None else primary_key)


    def load_nodes_from_list(self, nodes, label):
        """
            load nodes into the database
            
            @param nodes
                :type list
                :description: list of nodes

            @param label
                :type string
                :description: node label used for grouping
        """
        for node in nodes:
                self.node_dict[node.id] = Node(label,**(node.__dict__))
        
    def load_edges_from_list(self, edges, type = "TO"):
        """
            space efficiently load edges into the database
            returns a generator that must be consumed with iteration
            
            @param edges
                :type list
                :description: list of edges

            @param type
                :type string
                :description: relationship type between the nodes

            :rtype generator
        """
        if not isinstance(edges, list) or not isinstance(edges[0], tuple):
            raise TypeError("edges must be a list of tuple")

        for edge in edges:
            # check if the edge has attribute
            if len(edge) > 2:
                start_node , end_node, attribute_dict = edge
            else:
                start_node , end_node = edge
                attribute_dict = {}

            # check if the start node in this edge is in the loaded nodes
            if start_node.id not in self.node_dict:
                # create the node if it is not in the node list
                start_node = Node(start_node.type, **(start_node.__dict__))                
            else:
                start_node = self.node_dict[start_node.id]

            # check if the end node in this edge is in the loaded nodes
            if  end_node.id not in self.node_dict:
                # create the node if it is not in the node list
                end_node = Node(end_node.type, **(end_node.__dict__))
            else:
                end_node = self.node_dict[end_node.id]
            
            rel = Relationship(start_node, type, end_node)
            for k, v in attribute_dict.items():
                rel[k] = v
           
            yield rel
        
    def load_nodes_from_file(self, fp, header_file, label = None):
        """
            Loads nodes from file

            @param fp
                :type File
                :description: an open csv file object
            
            @param header
                :type list
                :description: list of column names in the csv file
            
            @param label
                :type string
                :description: node label used for grouping

        """
        header = []        
        reader = csv.reader(header_file)
        for row in reader:
            header += row
        
        # header must contain :ID field
        if ":ID" not in header:
            raise Exception("Header must have :ID column")

        reader = csv.reader(fp)
        rows = []

        for row in reader:
            rows.append(zip(header, row))
        
        if label == None:
            self.label = row[-1]
        else:
            self.label = label

        for row in rows:
            node = Node(self.label)
            for k, v in row:
                if k == ":ID":
                    node[self.__key] = v
                else:
                    node[k] = v

            self.node_dict[node[self.__key]] = node

        return self.node_dict.values()

    def load_edges_from_file(self, fp, header_file, type = "TO"):
        """
            Loads nodes from file

            @param fp
                :type File
                :description: an open csv file object
            
            @param header
                :type list
                :description: list of column names in the csv file
            
            @param type
                :type string
                :description: specifies the type of connection

        """
        header = []        
        reader = csv.reader(header_file)
        for row in reader:
            header += row

        if self.__start not in header or self.__end not in  header or self.__type not in header:
            raise Exception("Invalid edge header")

        reader = csv.reader(fp)
        rows = []

        for row in reader:
            rows.append(zip(header, row))

        for row in rows:
            row = list(row)
            start = row.pop(0)
            end = row.pop(-2)
            _type = row.pop(-1)

            # checks if the header is properly formatted
            if start[0] != self.__start or end[0] != self.__end or _type[0] != self.__type:
                print("Header format => :START_ID,<properties ...>,:END_ID,:TYPE")
                raise Exception("Invalid header format")
            
            # the node is not in node dict skip
            if start[1] not in self.node_dict.keys() or  end[1] not in self.node_dict.keys():
                continue

            start_node = self.node_dict[start[1]]
            end_node = self.node_dict[end[1]]
            rel = Relationship(start_node, type, end_node)

            for k, v in row:
                rel[k] = v
            self.rels.append(rel)

        return self.rels

    def writeToDb(self):
        """
            writes the loaded information to database
        """
        for n in self.node_dict.values():
            self.graph.merge(n, self.label, self.__key)

        for rel in self.rels:
            self.graph.create(rel)