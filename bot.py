import praw
import os
import json


client_secret = os.environ["CLIENT_SECRET"]
client_id = os.environ["CLIENT_ID"]
password = os.environ["PASSWORD"]
username = os.environ["USERNAME"]

user_agent = "python:evolutionconvo:v1.0.0 (by /u/%s)" % username


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
        self.created = comment.created
        self.id = comment.id
        self.body = comment.body
        self.sentiment = None # todo: update with sentiment analysis
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

    def dump_submission_comments(self, submission_id, filename):
        """
            @param submission_id
            @param filename
            write the comments in the submission with the given id
            to filename.
        """
        submission = self.reddit.submission(id=submission_id)
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
    bot.dump_submission_comments(submission_id, filename)
    # for c in bot.get_submissions():
    #     print(c)
    # print(len(bot.get_submissions()))
