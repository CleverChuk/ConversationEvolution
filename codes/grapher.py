import networkx as nx
from analyzers import CommentMetaAnalysis
from textsim import cosine_sim
from models import CommentNode, AuthorNode, Node, ArticleNode, SentimentNode
from base import RedditBot
import mapper_functions as mp
import neonx


def load_graph(filepath, type):
    """
        :type filepath: str
        :rtype Graph
    """
    return nx.read_graphml(filepath, node_type=type)


class GraphBot(RedditBot):
    """
        builds graph
    """

    @property
    def main_graph(self):
        if self._main_graph == None:
            raise Exception("You have to call getGraph(...) first")

        return self.main_graph

    @property
    def comment_graph(self):
        if self._main_graph == None:
            raise Exception("You have to call getGraph(...) first")

        return self._comment_graph

    @main_graph.setter
    def main_graph(self, value):
        self._main_graph = value

    @comment_graph.setter
    def comment_graph(self, value):
        self._comment_graph = value

    def __init__(self, subreddit, username="CleverChuk", password="BwO9pJdzGaVj2pyhZ4kJ"):
        self._ids = None
        super().__init__(subreddit, username, password)

        self._main_graph = None
        self._comment_graph = None
        self.group_graph = None

    def stream(self, subreddit):
        """
            streams graphs from the given subreddit 
        """
        stream = self.reddit.subreddit(subreddit).stream
        for submission in stream.submissions():
            yield self.getGraph(submission.id)

    def getGraph(self, *ids):
        """"
            builds graph from article with submission id
        """
        self._ids = ids  # save the ids for future queries
        sentiment = {"Positive": SentimentNode("Positive"), "Negative": SentimentNode(
            "Negative"), "Neutral": SentimentNode("Neutral")}
        article_comment_edges = []  # article/comment edge
        comment_comment_edges = []  # undirected comment/comment edges
        sentiment_comment_edges = []  # sentiment/comment edges
        nodes = []
        # create a digraph for comment/comment edges
        diGraph = nx.DiGraph()

        # create a graph object
        graph = nx.Graph()

        for id in ids:
            try:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)
                article_node = ArticleNode(submission)

                # populate article/comment edge list
                for comment in submission.comments.list():
                    article_comment_edges.append((
                        CommentNode(comment, CommentMetaAnalysis(
                            comment)), article_node,
                        {"type": "article-comment"}
                    ))
            except Exception as pe:
                print(pe)

        # populate sentiment/comment  and comment/comment edge list
        for p_comment, _,  *_ in article_comment_edges:
            sentiment_comment_edges.append((sentiment[p_comment.sentiment], p_comment, {
                "score": p_comment.sentiment_score, "type": "sentiment-comment"}))

            for c_comment, _,  *_ in article_comment_edges:
                if c_comment.parent_id == p_comment.id:
                    # nx does not support numpy float
                    c_comment.similarity = round(
                        float(cosine_sim(p_comment.body, c_comment.body)), 4)
                    comment_comment_edges.append((c_comment, p_comment,
                                                  {"type": "parent-child", "similarity": c_comment.similarity}))

        author_comments_edges = []
        for comment, _, *_ in article_comment_edges:
            author_comments_edges.append(
                (AuthorNode(comment.author), comment, {"type": "author-comment"}))

        # add nodes and node attributes
        for cc, pc, *_ in comment_comment_edges:
            nodes.append((pc, pc.__dict__))
            nodes.append((cc, cc.__dict__))

        diGraph.add_nodes_from(nodes)

        for _, a, *_ in article_comment_edges:
            nodes.append((a, a.__dict__))

        for _, v in sentiment.items():
            nodes.append((v, v.__dict__))

        for item in author_comments_edges:
            author, *_ = item
            nodes.append((author, author.__dict__))

        diGraph.add_edges_from(comment_comment_edges)

        graph.add_edges_from(author_comments_edges)
        graph.add_edges_from(comment_comment_edges)
        graph.add_edges_from(article_comment_edges)
        graph.add_edges_from(sentiment_comment_edges)
        graph.add_nodes_from(nodes)

        # full graphs
        self._comment_graph = diGraph
        self._main_graph = graph

        # high level graphs
        self.group_graph = mp.clusterOnNumericProperty(20, comment_comment_edges,prop="timestamp")

        return graph


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from models import CustomEncoder
    # "9bdwe3","9f3vyq","9f4lcs"
    subreddit = "legaladvice"
    filename = "./raw/%s.json" % subreddit
    # username = input("Enter username:")
    # password = input("Enter password(Not hidden, so make sure no one is looking):")

    bot = GraphBot(subreddit)
    ids = list(bot.get_hot_submissions(1))
    graph = bot.getGraph(*ids)

    bot.dump(filename, ids)
    nx.write_graphml(graph, "./graphML/reddit_graph_%s.graphml" % subreddit)
    nx.write_graphml(bot.comment_graph,
                     "./graphML/comment_graph_%s.graphml" % subreddit)
    nx.write_graphml(bot.group_graph, "./graphML/interval_graph.graphml")

    # data = neonx.get_geoff(graph, "LINKS_TO", CustomEncoder())
    # nx.write_gexf(graph,"./graphML/neo.gexf")
    # neonx.write_to_neo("http://localhost:7687",graph,"LINKS_TO", encoder=CustomEncoder())
    # for g in bot.stream(subreddit):
    #     print(nx.clustering(g))
    # nx.draw(graph, with_labels=False, font_weight='bold')
    # plt.show()
    # bot.dump_submission_comments(submission_id, filename)
