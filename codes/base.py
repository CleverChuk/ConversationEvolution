# Author: Chukwubuikem Ume-Ugwa
# Purpose: Class use to pull data from Reddit
import json
from json_models import SubmissionDump, CustomEncoder
import praw



class RedditBot:
    def __init__(self, subreddit, username="CleverChuk", password="BwO9pJdzGaVj2pyhZ4kJ", APP_NAME = "myapp", VERSION = "1.0.0"):
        """ 
            initialize the bot

            @param subreddit
                :type string
                :description: the name of the subreddit to get data from
        
            @param username
                :type string
                :description: Reddit username
            
            @param subreddit
                :type string
                :description: Reddit password

        """
        self._client_secret = "dcnGfpdIFWH-Zk4Vr6mCypz1dmI"
        self._client_id = "n-EWVSgG6cMnRQ"
        self.user_agent = "python:%s:v%s (by /u/%s)" % (APP_NAME,VERSION,username)

        self.reddit = praw.Reddit(client_id=self._client_id, client_secret=self._client_secret,
                                  password=password, user_agent=self.user_agent, username=username)
        self.subreddit = self.reddit.subreddit(subreddit)

    def get_submissions(self):
        """
            get all submission ids in a subreddit.

            :rtype List
        """
        return list(set(comment.submission.id for comment in self.subreddit.comments()))

    def get_hot_submissions_id(self, limit=10):
        """
            gets hot articles from the subreddit
            
            @param limit
                :type int
                :description: number of submissions to get

            :rtype List: of tuple (title, score).
        """
        for submission in self.subreddit.hot(limit=limit):
             yield submission.id

    def get_submission(self, id):
        """
            @param id
                :type string
                :description: Reddit submission id

            rtype: Reddit.Submission
        """
        return self.reddit.submission(id=id)

    def dumpjson(self, filename, ids):
        """
            write the comments in the submission with the given id
            to filename.
            
            @param ids
                :type list
                :description: list of Reddit submission ids
        

            @param filename
                :type string
                :description: name of the file to write json data
        """
        with open(filename, "w") as fp:
            data = []
            for id in ids:
                submission = self.get_submission(id)
                submission.comments.replace_more(limit=None)

                data.append(SubmissionDump(submission))

            json.dump(data, fp, separators=(',', ':'), cls=CustomEncoder, sort_keys=False, indent=4)

    def __repr__(self):
        return "RedditBot"
