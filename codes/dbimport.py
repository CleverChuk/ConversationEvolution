from py2neo import (Graph, Node, Relationship)
import csv
from models import (CommentNode)


class LoadNodes:
    def __init__(self, node_cls):
        self.node_cls = node_cls
        self.node_dict = {}

    def load(self, fp, header):
        # header must contain ID field
        reader = csv.reader(fp)
        rows = []

        for row in reader:
            rows.append(zip(header, row))

        for row in rows:
            node = self.node_cls()
            for k, v in row:
                node[k] = v
            self.node_dict[node[':ID']] = node

        return self.node_dict.values()

    def writeToDb(self, url="http://localhost:11002/", username="neo4j", password="chubi93"):
        g = Graph(url, username=username, password=password)        
        for n in self.node_dict.values():
            g.create(n)

class LoadRelationships:
    def __init__(self, rel_cls):
        self.rel_cls = rel_cls
        self.rels = []

    def load(self, fp, header):
        reader = csv.reader(fp)
        rows = []

        for row in reader:
            rows.append(zip(header, row))

        for row in rows:
            rel = self.rel_cls()
            for k, v in row:
                rel[k] = v
            self.rels.append(rel)

        return self.rels

    def writeToDb(self, url="http://localhost:11002/", username="neo4j", password="chubi93"):
        g = Graph(url, username=username, password=password)        
        for rel in self.rels:
            g.create(rel)

if __name__ == "__main__":
    ln = LoadNodes(Node)
    header = [":ID", "article_id", "parent_id", "author", "score", "timestamp", "length",
              "averageWordLength", "quotedTextPerLength", "readingLevel", "sentimentScore", "sentiment", "similarity", ":LABEL"]
    with open("raw/comment_data.csv", mode="r", newline="") as fp:
        ln.load(fp, header)
        ln.writeToDb()
