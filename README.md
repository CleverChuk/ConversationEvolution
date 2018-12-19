---
title: "Conversation Evolution"
author: "Chukwubuikem Ume-Ugwa"
date: "November 26, 2018"
output: html_document
---

## Introduction
This project consists of the backend codes for the Mapper software. There are two components of the project: **data gathering**, and **database integration**. Data gathering involves scraping data from Reddit and creating new data from the metadata of the data obtained. The data obtained include submissions, and comments. From these two data, I used the meta information to form the author and sentiment data. These data are represented using Python classes and can be modified to add more properties that will help with the analysis. The Reddit API allows you to access only publicly available data. The data integration part of the project involves transforming the raw data into graphs and loading it into a good graph database. The database that is currently being used to explore the data is Neo4j.

## Objectives
* Create a stable data pipeline for the Mapper software.

* Implement mapper functions.

## Modules
The project is divided into modules and each module consist of functions and/or classes. They are grouped by what they do.

| Module | Purpose                                                                                                                      |
| ------ | -----------------------------------------------------------------------------------------------------------------------------|
| *base.py* | contains the base class used to retrieve data from Reddit |
| *grapher.py* | contains the class that extends RedditBot|
| *analyzers.py* | consists of functions used to calculate data fields such as sentiment, number of quoted texts per length etc. |
| *textsim.py* | consist of functions for document analysis like similarity calculation |
| *graph_writer.py* | consist of functions that write graph to csv using Neo4j schema
| *mapper_functions.py* | consist of functions used create mapper graph
| *models.py* | consist of data models
| *json_decode.py* | consist of data models used to decode json
| *dbimport.py* | module used to import data into an existing database.
| *main.py*| entry point


## Classes
####Class RedditBot####
  
  **Object**
  
  `Direct Subclass`
  
  **Grapher**
  
This class is a wrapper of praw.Reddit. It is used to query the Reddit api for data.

This example creates a RedditBot object and uses it to get the subbmission ids of 10 hot submissions.

```Python
bot = RedditBot("compsci", "CleverChuk", "password")

ids = bot.get_hot_submissions_id(limit = 10)

ids = list(ids)

To dump the threads to json, use the following code:

bot.dumpjson("compsci.json", ids)
```

**Constructor Summary**

`RedditBot(subreddit, "username", "password")`

constructs a RedditBot with the given subreddit, username, password and APP_NAME w/ value "myapp" and VERSION w/ value "1.0.0"

`RedditBot(subreddit, username, password, APP_NAME)`

constructs a RedditBot with the given subreddit, username, password, APP_NAME and VERSION w/ value "1.0.0"

`RedditBot(subreddit, username, password, APP_NAME, VERSION)`

constructs a RedditBot with the given subreddit, username, password, APP_NAME and VERSION

**Method Summary**

Type | Method description
-----|--------------------------------------------------------------------------------------------------------------------------------
**list** | **get_submissions()**<br/>Returns a list of submission ids in the subreddit.
**Reddit.Submission** | **get_submission(id)**<br/>Returns a submission object.
**generator**|**get_hot_submissions_id(limit=10)**<br/>Returns a generator that yields 10 submission ids.
**None**|**dumpjson(filename, ids)**<br/> Dumps submissions with id in ids to json.


####Class Grapher####
  
  **Object**
  
  **RedditBot**
  
  `Direct Subclass`
  
  
This class is extends the RedditBot class and adds graphing capability by wrapping Networkx.Graph.

This example creates a Grapher object and uses it to generate a mapper graph and normal of the given subbmission ids.

```Python
intervals = 10

prop = "score"

epsilon = 0.05

ids = ["a55xbm","a57th7"]

subreddit = "programming"

grapher = Grapher(subreddit, "username", "password", intervals=intervals, property_key=prop, epsilon=epsilon)

graph = grapher.get_graph(*ids)
```

**Constructor Summary**

`Grapher(subreddit, username, password)`

constructs a Grapher with the given subreddit, username, password and defaults for intervals, property_key, epsilon,APP_NAME and VERSION

`Grapher(subreddit, username, password, intervals=10)`

constructs a Grapher with the given subreddit, username, password, and intervals

`Grapher(subreddit, username, password, intervals = 10, property_key = "reading_level", epsilon = 0.5)`

constructs a Grapher with the given subreddit, username, password, intervals, property_key and epsilon.

**Method Summary**

Type | Method description
-----|--------------------------------------------------------------------------------------------------------------------------------
**boolean** | **is_removed(comment)**<br/>Returns true if the comment has been removed otherwise false.
**generator** | **stream(subreddit)**<br/>Returns a generator that yields submission graphs from the subreddit.
**Networkx.Graph**|**get_graph(ids)**<br/>Builds graph from the submission ids.
**Networkx.Graph**|**load_graph(filename, node_type)**<br/>Loads a graph from a .graphml file.


####Class Loader####
  
  **Object**
  
  `Direct Subclass`
  
  
This class is a wrapper of py2neo.Graph and is used to import Nodes and edges into an existing database.

This example creates a Loader object and uses it to import nodes and edges from both CSV files and list .

```Python
# loader
loader = Loader("url", "username", "password")

# load from list
loader.write_nodes_from_list(comment_nodes,"comment")
loader.write_edges_from_list(comment_comment_edges,type="REPLY_TO")  

# load from files
with open("node_data.csv", mode="r", newline="") as fp:        
    with open("edge_data.csv", mode="r", newline="") as fp0:
        with open("node_header.csv") as node_header:
            with open("edges_header.csv") as rel_header:
                loader.load_nodes_from_file(fp, node_header, label = 'comment')
                loader.load_edges_from_file(fp0, rel_header, type = "REPLY_TO")  
                loader.writeToDb()
```

**Constructor Summary**

`Loader(db_url, username, password)`

constructs a Loader object with the given database url, username, password.

**Method Summary**

Type | Method description
-----|--------------------------------------------------------------------------------------------------------------------------------
**None** | **load_nodes_from_list(nodes, label)**<br/>Writes the nodes into the database.
**generator** | **load_edges_from_list(edges, type = "TO")**<br/>Returns a generator that yields py2neo.Relationship objects.
**None**|**load_nodes_from_file(fp, header_file, label = None)**<br/>Loads the nodes in the given file(fp).
**None**|**load_edges_from_file(fp, header_file, type = "TO")**<br/>Loads the edges in the given file(fp).
**None**|**write_to_db()**<br/>writes the loaded nodes and edges to database.


####Class CommentAnalyzer####
  
  **Object**
  
  `Direct Subclass`
  
  
This class is used to calculate derived attributes of a comment.

This example creates a CommentAnalyzer object and access the value of the derived attributes.

```Python
comment = "Do you even know what you're talking about?"
analyzer = CommentAnalyzer(comment)
length = analyzer.length()
reading_level = analyzer.reading_level()
```


**Constructor Summary**

`CommentAnalyzer(comment)`

constructs a CommentAnalyzer object with the given comment.

**Method Summary**

Type | Method description
-----|--------------------------------------------------------------------------------------------------------------------------------
**int** | **length()**<br/>Gets the number of characters in the comment.
**float** | **quoted_text_per_length()**<br/>Calculates the amount of quoted text per length of comment.
**float**|**average_word_length()**<br/>Calculates the average word length of a comment.
**float**|**reading_level()**<br/>Calculates the reading level of the comment.

####Class SentimentAnalyzer####
  
  **Object**
  
  `Direct Subclass`
  
  
This class is used to calculate the sentiment of a given comment using the Vader SentimentIntensityAnalyzer algorithm found in NLTK module.

This example uses the class method of SentimentAnalyzer to calculate the sentiment of a comment.

```Python
comment = "Do you even know what you're talking about?"
sentiment_score = SentimentAnalyzer.get_sentiment(comment)
sentiment = SentimentAnalyzer.convert_score(sentiment_score)
print(sentiment)
```

**Method Summary**

Type | Method description
-----|--------------------------------------------------------------------------------------------------------------------------------
**list** | **find_sentence(text)**<br/>Extract the sentences from the text.
**string** | **convert_score(score)**<br/>Convert numeric sentiment score to a text.
**float**|**get_sentiment(comment)**<br/>Calculates the mean score for all the sentences in a comment.
**float**|**sentiment(sentence)**<br/>Calculates the sentiment of the given sentence.

**Miscellaneous Modules**

- mp_test.py

- redditor_attribute.py

- api/*

- neo4j/*

## Setup
1. Download and [install](https://neo4j.com/download/) Neo4j database

2. Download and install the Python packages in the _Non-standard Python Modules Used in this Project._ section.

3. Create a Reddit account

4. Log into your Reddit account and do the following:
  
    1. Click on your username
    
    2. In the dropdown menu click on _User Settings_
    
    3. On the new page, click on _Privacy & Security_
    
    4. On the new page, Click on _App Authorization_
    
    5. Click on _create App_ or _Create Another App_ if you already have one. 
    
    6. Note the app secret and client id.
  
5. In main.py module, provide the GraphBot constructor with the required input

6. Execute main.py
    

## Data Collection
Data collection is done using APIs found in Praw. [`Praw`](https://praw.readthedocs.io/en/latest/index.html) is a Reddit API wrapper that can be used to scrape data from Reddit. Reddit API rules can be found [here](https://github.com/reddit-archive/reddit/wiki/API).

## Graph
Graph generation is done using [`Networkx`](https://networkx.github.io/documentation/stable/index.html) APIs. Networkx is used to write graph in graphml format, while CSV graph format is generated using Neo4j schema and is implemented in [graph_writer.py] (#Introduction) module.

## Neo4j Database
There are two core record types in Neo4j, the node and relationship. The node represents a graph's vertex while the relationship represents a graph's edge. Both the nodes and the relationships can have zero or more properties. Neo4j use labels to distinguish between different nodes and types to distinguish relationships.

**Some notes on Neo4j**

* Neo4j groups nodes and relationship in the database based on an assigned label on creation time.

* Every relationship in Neo4j is directed.

* Creating a constraint also creates and index and removing a constraint removes an index created by the constraint.

* Cannot create an index and then create a constraint that uses that index. The constraint must be created first which then creates the index.

* If using the import tool:

  
    - Data must be in CSV format
    
    - Each node data import must have a header.
    
    - Node header and data file must have the ID field.
     
    - Each edge(relationship) data import must also have a header
    
    - Edge header and data files must have START_ID, END_ID and TYPE fields.

Go [here](https://neo4j.com/docs/operations-manual/3.5/tools/import/file-header-format/#import-tool-header-format-nodes) for more details on data import

**Indexes in Neo4j**

- takes up storage space

- causes slower write operation

*Types of Indexes*

- Single-Property index: ```CREATE INDEX ON :<node label> (<node property>) ```

- Composite-Property index: ```CREATE INDEX ON :<node label> (<prop 1, prop2,>) ```

**Constraint in Neo4j**
 A constraint is a specification that a data being added to the database must meet to be considered valid data. In a nutshell, a data filter.
 
 *Types of Constraints*
 
 - Unique property constraint
 
 - Property existence constraint
 
## Neo4j CYPHER

[Cypher](https://neo4j.com/developer/cypher-query-language/) is the query language for Neo4j graph database. [Check out](https://neo4j.com/docs/cypher-refcard/current/) the Cypher Reference card for quick references on the Cypher language.

**Key Features**

- Uses patterns to describe graph data

- SQL-like clauses

- Declarative

**Some Notes on Cypher**

- node-labels, relationship-types and property-names are case-sensitive in Cypher.
- all queries must return one or more value


## Neo4j API ENDPOINTS
Neo4j database API endpoints follow this format: <HTTP HTTPs>://<host>:<port>/db/data/transaction/[commit]. The commit is optional is optional if you intend to keep the transaction open. The server will return a transaction endpoint in its response if commit is missing and will timeout the after 60 seconds. Transaction timeout can be reset by sending a request with empty statement and the timeout length can be modified in the database config.

Example API request to this endpoint is shown below. The below request will execute the statements and close the transaction due to having commit in the URL. More examples can be found [here](https://neo4j.com/docs/developer-manual/3.4/http-api/).

    POST http://localhost:7474/db/data/transaction/commit
    Accept: application/json; charset=UTF-8
    Content-Type: application/json

    {
      "statements": [ {
        "statement": "CREATE (n) RETURN id(n)"
      }, {
        "statement": "CREATE (n {props}) RETURN n",
        "parameters": {
          "props": {
            "name": "My Node"
          }
        }
      } ]
    }

**Interacting with Database with Py2neo**

[`Py2neo`](https://py2neo.org/v4/) is a Python library for working with Neo4j databases. It wraps the official Neo4j driver and provides a higher-level API for interacting with the database.

*Example: interaction*
```Python
  from py2neo import *
  from pandas import DataFrame
  # get a graph object
  graph = Graph ("http://localhost:11002", username="neo4j", password="password")
  
  # get all nodes in db
  cursor = graph.run("MATCH(n) RETURN n")
  data = cursor.data ()
  
  # display data
  DataFrame(data)
```
**Loading data into an existing db**

Use the Loader class in dbimport.py
 
```Python
# create the loader class
loader = Loader(url="http://localhost:11002/", username="neo4j", password="password")
# load from files
# node csv header with mandatory ":ID" field
node_header = [":ID","article_id","parent_id","is_root","author", "score", "timestamp", "length", "averageWordLength",
"quotedTextPerLength","readingLevel","sentimentScore","sentiment","similarity"]
# edge csv header with mandatory fields
rel_header = [":START_ID","id","similarity",":END_ID",":TYPE"]
with open("raw/comment_nodes.csv", mode="r", newline="") as fp:        
    with open("raw/comment_edges.csv", mode="r", newline="") as fp0:
        loader.load_nodes_from_file(fp,node_header)
        loader.load_edges_from_file(fp0, rel_header)  
        loader.writeToDb()

node_header = [":ID","name"]
rel_header = [":START_ID","id",":END_ID",":TYPE"]
with open("raw/author_nodes.csv", mode="r", newline="") as fp:        
    with open("raw/author_comment_edges.csv", mode="r", newline="") as fp0:
        loader.load_nodes_from_file(fp,node_header)
        loader.load_edges_from_file(fp0, rel_header, type="WROTE")  
        loader.writeToDb()
```

## Non-standard Python Modules Used in this Project.
- [`NetworkX`](https://networkx.github.io/documentation/stable/index.html)
- [`Praw`](https://praw.readthedocs.io/en/latest/index.html)
- [`NLTK`](https://www.nltk.org/)
- [`SKLearn`](https://scikit-learn.org/stable/)
- [`Py2neo`](https://py2neo.org/v4/)

