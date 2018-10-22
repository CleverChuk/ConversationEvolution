
import os
import json
from models import Submission, CustomEncoder
import praw



class RedditBot:
    def __init__(self, subreddit, username="CleverChuk", password="BwO9pJdzGaVj2pyhZ4kJ"):
        """ 
            initialize the bot
        """
        self._client_secret = "dcnGfpdIFWH-Zk4Vr6mCypz1dmI"
        self._client_id = "n-EWVSgG6cMnRQ"
        self.user_agent = "python:evolutionconvo:v1.0.0 (by /u/%s)" % username

        self.reddit = praw.Reddit(client_id=self._client_id, client_secret=self._client_secret,
                                  password=password, user_agent=self.user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def get_submissions(self):
        """
            get all submission ids in a subreddit.

            :rtype List
        """
        return list(set(comment.submission.id for comment in self.subreddit.comments()))

    def get_hot_submissions(self, limit=10):
        """
            :type int:limit number of submissions to get

            :rtype List: of tuple (title, score).
        """
        return [(submission.title, submission.score) for submission in self.subreddit.hot(limit=limit)]

    def get_submission(self, id):
        """
            rtype: Reddit.Submission
        """
        return self.reddit.submission(id=id)

    def dump(self, filename, ids):
        """
            @param submission_id

            @param filename
            
            write the comments in the submission with the given id
            to filename.
        """
        with open(filename, "w") as fp:
            for id in ids:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)

                sub = Submission(submission)
                json.dump(sub, fp, separators=(',', ':'),
                        cls=CustomEncoder, sort_keys=False, indent=4)

    def __repr__(self):
        return "RedditBot"


# if __name__ == "__main__":
#     subreddit = "compsci"
#     filename = "../raw/data.json"
#     submission_id = "9bdwe3"
#     bot = RedditBot(subreddit)
#     bot.dump(submission_id, filename)
