from libs.database_api import *
from libs.layouts import *

import unittest

# Create db layer object and pass it to the query object
db_layer = Neo4jLayer()
query = Query(db_layer)


class TimeLayoutTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tested = TimeGraphLayout(None)
        data = query.get_comments_in_article('f3ejzj')
        self.tested.add_edges(data)

    def test_layout_igraph(self):
        self.tested.layout_igraph("fr")
