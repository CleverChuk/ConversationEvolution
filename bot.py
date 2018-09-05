import praw
import os
import json


client_secret = os.environ["CLIENT_SECRET"]
client_id = os.environ["CLIENT_ID"]
password = os.environ["PASSWORD"]
username = os.environ["USERNAME"]
user_agent = "python:evolutionconvo:v1.0.0 (by /u/cleverchuk)"



class CustomeEncoder(json.JSONEncoder):
    """
        Custom encoder for comment class
    """

    def default(self, o):
        return  o.__dict__

    def decode_object(self, o):
        pass

class Submission:
    def __init__(self, id, submission):
        self.id = id
        self.comments = [Comment(comment) for comment in submission.comments]


class Comment:
    """
        Encapsulates all comments
    """

    def __init__(self, comment):
        self.id = comment.id
        self.body = comment.body
        self.replies = [Comment(c) for c in comment.replies]


class RedditBot:
    def __init__(self, subreddit):
        """ 
            initialize the bot
        """
        self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password,
                                  user_agent=user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def get_all_comments(self):
        """
            get all comments in subreddit.
        """
        for comment in self.subreddit.comments():
            yield comment.body

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
            sub = Submission(submission_id, submission)
            json.dump(sub, fp, separators=(',', ':'),
                      cls=CustomeEncoder, sort_keys=True, indent=4)

    def __repr__(self):
        return "RedditBot"


if __name__ == "__main__":
    subreddit = "compsci"
    filename = "data.json"
    submission_id = "9bdwe3"
    bot = RedditBot(subreddit)
    bot.dump_submission_comments(submission_id, filename)
