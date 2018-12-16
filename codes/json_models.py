from json import JSONEncoder
from analyzers import  SentimentAnalysis

class CustomEncoder(JSONEncoder):
    """
        Custom encoder for comment class
    """
    def default(self, o):
        return o.__dict__

    def decode_object(self, o):
        pass


class Submission:
    def __init__(self,obj):
        self.author_fullname = obj.pop("author_fullname","na")
        self.id = obj.pop("id","na")
        self.title = obj.pop("title","na")
        self.view_count = obj.pop("view_count","na")
        self.upvote_ratio = obj.pop("upvote_ratio","na")
        self.ups = obj.pop("ups","na")
        self.downs = obj.pop("downs","na")
        self.comments = [Comment(comment) for comment in obj.pop("comments",[])]

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
        self.average_word_length =  obj.pop("average_word_length","na")
        self.quoted_text_per_length =  obj.pop("quoted_text_per_length","na")
        self.reading_level =  obj.pop("reading_level","na")
        self.sentiment_score =  obj.pop("sentiment_score","na")
        self.sentiment =  obj.pop("sentiment","na")
        self.is_root = obj.pop("is_root",False)
        self.replies = [Comment(c) for c in  obj.pop("replies",[])]

    def __repr__(self):
        return self.body

class SubmissionDump:
    """
        submission object use to write to json
    """
    def __init__(self, submission):
        self.author_fullname = submission.author_fullname if hasattr(submission,"author_fullname") else "Anonymous"
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count
        self.upvote_ratio = submission.upvote_ratio
        self.ups = submission.ups
        self.downs = submission.downs
        self.comments = [CommentDump(comment) for comment in submission.comments]
    
    def __repr__(self):
        return self.title

class CommentDump:
    """
        comment object used to write to json
    """
    def __init__(self, comment):
        from analyzers import CommentAnalysis
        meta_analyzer = CommentAnalysis(comment)
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.parent_id = comment.parent().id
        self.score = comment.score
        self.timestamp = comment.created
        self.id = comment.id
        self.body = comment.body
        self.length = meta_analyzer.length
        self.average_word_length = meta_analyzer.average_word_length
        self.quoted_text_per_length = meta_analyzer.quoted_text_per_length
        self.reading_level = meta_analyzer.reading_level
        self.sentiment_score = SentimentAnalysis.get_sentiment(comment)
        self.sentiment = SentimentAnalysis.convert_score(self.sentiment_score)
        self.replies = [CommentDump(c) for c in comment.replies]

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
