// Load comment nodes
Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/comment_data.csv" AS line Merge
 (comment:Comment {type:line.type, id:line.id,author:line.author, reading_level:line.readingLevel,
 parent_id:line.parent_id, length:line.length, sentiment:line.sentiment, article_id:line.article_id });

 // Load author nodes
Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/author_data.csv" AS line Merge
 (author:Author {type:line.type, name:line.name });

// Load article nodes
Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/article_data.csv" AS line Merge 
(article:Article {title:line.title,type:line.type, id:line.id, upvote_ratio:line.upvote_ratio });

// Load sentiment nodes
Load CSV WITH HEADERS FROM 
"file:///C:/Users/chubi/Desktop/Fall%2018/REU/ConversationEvolution/raw/sentiment_data.csv" AS line Merge
(sentiment:Sentiment {type:line.type, sentiment:line.value});

// Connect comment and comment
match (c1:Comment),(c2:Comment) where c1.parent_id = c2.id create (c1)-[r:REPLY_TO]->(c2) return c1,c2;
// Connect article and comment
Match(a:Article),(c:Comment) where a.id = c.article_id create (c)-[r:BELONGS_TO]->(a) return a,c;
//Connect sentiment and comment
Match(s:Sentiment),(c:Comment) where s.sentiment = c.sentiment create (c)-[r:_IS]->(s) return s,c;
//Connect Author and Comment
Match(a:Author),(c:Comment) where a.name = c.author create (a)-[r:WROTE]->(c) return a,c;
// Get some data
MATCH (n1)-[r]->(n2) RETURN r, n1, n2;
// Empty database
match(n) detach delete n;




// Empty database
match(n) detach delete n