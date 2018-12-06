from py2neo import (Graph, Node, Relationship)
import csv
from models import (CommentNode)

class Loader:    
    """
        Class used to import Nodes and edges into an existing database
    """

    def __init__(self, url="http://localhost:11002/", username="neo4j", password="chubi93"):
        """
            @param url
                :type String
                :description: a class name
        """
        self.node_dict = {}
        self.rels = []
        self.__start = ":START_ID"
        self.__end = ":END_ID"
        self.__type = ":TYPE"
        self.__key = "key"

        self.label = None
        self.graph = Graph(url, username = username, password = password)

    def load_nodes(self, fp, header, label = None):
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


    def load_edges(self, fp, header, type = "TO"):
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
        for n in self.node_dict.values():
            self.graph.merge(n, self.label, self.__key)

        for rel in self.rels:
            self.graph.create(rel)