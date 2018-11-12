Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/comment_data.csv" 
AS line Merge (comment:Comment { 
    id:line.id, author:line.author, 
    reading_level:line.readingLevel, 
    parent_id:line.parent_id, 
    length:line.length, 
    sentiment:line.sentiment, 
    article_id:line.article_id });

match (c1:Comment),(c2:Comment) where c1.parent_id = c2.id create (c1)-[r:REPLY_TO]->(c2) return c1,c2;

Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/author_data.csv" 
AS line Merge (author:Author { name:line.name });

Load CSV WITH HEADERS FROM
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/article_data.csv" 
AS line Merge (article:Article {title:line.title, id:line.id, upvote_ratio:line.upvote_ratio });

Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/sentiment_data.csv" 
AS line Merge (sentiment:Sentiment {sentiment:line.sentiment});

Match(a:Article),(c:Comment) where a.id = c.article_id create (c)-[r:BELONGS_TO]->(a) return a,c;
Match(s:Sentiment),(c:Comment) where s.sentiment = c.sentiment create (c)-[r:_IS]->(s) return s,c;
Match(a:Author),(c:Comment) where a.name = c.author create (a)-[r:WROTE]->(c) return a,c;