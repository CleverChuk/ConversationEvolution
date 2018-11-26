class Submission:
    def __init__(self,obj):
        self.author_fullname = obj["author_fullname"]
        self.id = obj["id"]
        self.title = obj["title"]
        self.view_count = obj["view_count"]
        self.upvote_ratio = obj["upvote_ratio"]
        self.ups = obj["ups"]
        self.downs = obj["downs"]
        self.comments = [Comment(comment) for comment in obj["comments"]]

    def __repr__(self):
        return self.title

class Comment:
    def __init__(self, obj):
        self.author =  obj["author"]
        self.parent_id = obj["parent_id"]
        self.score =  obj["score"]
        self.timestamp =  obj["timestamp"]
        self.id =  obj["id"]
        self.body =  obj["body"]
        self.length =  obj["length"]
        self.averageWordLength =  obj["averageWordLength"]
        self.quotedTextPerLength =  obj["quotedTextPerLength"]
        self.readingLevel =  obj["readingLevel"]
        self.sentimentScore =  obj["sentimentScore"]
        self.sentiment =  obj["sentiment"]
        self.replies = [Comment(c) for c in  obj["replies"]]

    def __repr__(self):
        return self.body