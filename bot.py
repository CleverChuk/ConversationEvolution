
import os
import json
import nltk
from statistics import mean
import re
import praw
import networkx as nx

UPPER_BOUND = 0.05
LOWER_BOUND = -0.05

client_secret = "dcnGfpdIFWH-Zk4Vr6mCypz1dmI"
client_id = "n-EWVSgG6cMnRQ"
username = "Cleverchuk" #input("Enter username:")
password = "BwO9pJdzGaVj2pyhZ4kJ" #input("Enter password(Not hidden, so make sure no one is looking):") 
user_agent = "python:evolutionconvo:v1.0.0 (by /u/%s)" % username

class SentimentAnalysis:
    def __init__(self):
        pass
    
    def find_sentence(text):
        """
            extract the sentences from the text
        """
        text = text.replace('\n','')
        pattern = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
        result = pattern.findall(text)
        result = result if len(result) > 0 else text
        return result 
    
    
    def convert_score(score):
        """
            convert the score to a word
            Positive for scores >= 0.05
            Negative for scores <= -0.05
            Neutral for scores that fall in between
        """
        if score is None:
            return None
        elif score >= UPPER_BOUND:
            return "Positive"
        elif score <= LOWER_BOUND:
            return "Negative"
        else:
            return "Neutral"

    
    def add_sentiment(comment):
        """
            returns the mean score for all the sentences in 
            a comment.
        """
        sentences = SentimentAnalysis.find_sentence(comment.body)
        scores = [SentimentAnalysis.sentiment(sentence) for sentence in sentences]

        return round(mean(scores),4) if len(scores) > 0 else None
        

    def sentiment(sentence):
        """
            returns a dictionary of the form
            {
                'neg': 0.0,
                'neu': 0.725,
                'pos': 0.275,
                'compound': 0.6908
            }
            this is a dictionary of sentiment scores
            we're interested in the compound score
        """
        from nltk.sentiment.vader import SentimentIntensityAnalyzer    
        nltk_sentiment = SentimentIntensityAnalyzer()    
        score = nltk_sentiment.polarity_scores(sentence)['compound'] 
        
        return score

class CustomeEncoder(json.JSONEncoder):
    """
        Custom encoder for comment class
    """
    def default(self, o):
        return o.__dict__

    def decode_object(self, o):
        pass


class Submission:
    """
        submission object
    """
    def __init__(self,submission):
        self.author_fullname = submission.author_fullname
        self.id = submission.id
        self.title = submission.title
        self.view_count = submission.view_count
        self.upvote_ratio = submission.upvote_ratio
        self.ups = submission.ups
        self.downs = submission.downs
        self.comments = [Comment(comment) for comment in submission.comments]


class Comment:
    """
        comment object
    """

    def __init__(self, comment):
        self.author = "Anonymous" if comment.author == None else comment.author.name
        self.score = comment.score
        self.timestamp = comment.created
        self.id = comment.id
        self.body = comment.body
        self.sentiment_score = SentimentAnalysis.add_sentiment(comment)
        self.sentiment = convert_score(self.sentiment_score)
        self.replies = [Comment(c) for c in comment.replies]


class RedditBot:
    def __init__(self, subreddit):
        """ 
            initialize the bot
        """
        self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password,
                                  user_agent=user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def get_submissions(self):
        """
            get all comments in subreddit.
        """
        return set(comment.submission for comment in self.subreddit.comments())
        

    def get_hot_submissions(self, limit=10):
        """
            @param: limit number of submissions to get
            return a list of tuple of title and score.
        """
        return [(submission.title, submission.score) for submission in self.subreddit.hot(limit=limit)]

    def get_submission(self, id):
        return self.reddit.submission(id=id)

    def dump_submission_comments(self, submission_id, filename):
        """
            @param submission_id
            @param filename
            write the comments in the submission with the given id
            to filename.
        """
        submission = self.get_submission(submission_id)
        submission.comments.replace_more(limit=None)

        with open(filename, "w") as fp:
            sub = Submission(submission)
            json.dump(sub, fp, separators=(',', ':'),
                      cls=CustomeEncoder, sort_keys=False, indent=4)

    def __repr__(self):
        return "RedditBot"


if __name__ == "__main__":
    subreddit = "compsci"
    filename = "data.json"
    submission_id = "9bdwe3"
    bot = RedditBot(subreddit)
    # bot.dump_submission_comments(submission_id, filename)

