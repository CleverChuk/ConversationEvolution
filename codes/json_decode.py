class Submission:
    def __init__(self,obj):
        self.author_fullname = obj.pop("author_fullname","na")
        self.id = obj.pop("id","na")
        self.title = obj.pop("title","na")
        self.view_count = obj.pop("view_count","na")
        self.upvote_ratio = obj.pop("upvote_ratio","na")
        self.ups = obj.pop("ups","na")
        self.downs = obj.pop("downs","na")
        self.comments = [Comment(comment) for comment in obj.pop("comments","na")]

    def __repr__(self):
        return self.title

class Comment:
    def __init__(self, obj):
        self.author =  obj.pop("author","na")
        self.parent_id = obj.pop("parent_id","na")
        self.score =  obj.pop("score","na")
        self.timestamp =  obj.pop("timestamp","na")
        self.id =  obj.pop("id","na")
        self.body =  obj.pop("body","na")
        self.length =  obj.pop("length","na")
        self.averageWordLength =  obj.pop("averageWordLength","na")
        self.quotedTextPerLength =  obj.pop("quotedTextPerLength","na")
        self.readingLevel =  obj.pop("readingLevel","na")
        self.sentimentScore =  obj.pop("sentimentScore","na")
        self.sentiment =  obj.pop("sentiment","na")
        self.replies = [Comment(c) for c in  obj.pop("replies","na")]

    def __repr__(self):
        return self.body

# how to decode json data with the above objects.
# if __name__ == "__main__":
#     import json
#     with open("./raw/legaladvice.json","r") as fp:
#         data = json.load(fp)
    
#     submissions = []
#     for s in data:
#         submissions.append(Submission(s))

#     for s in submissions:
#         for c in s.comments:
#             print(c)
