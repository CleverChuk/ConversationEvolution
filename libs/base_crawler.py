# Author: Chukwubuikem Ume-Ugwa
# Purpose: Class use to pull data from Reddit
import json
from json_models import SubmissionDump, CustomEncoder
import praw


class RedditBot:
    def __init__(self, subreddit, credential, APP_NAME="myapp", VERSION="1.0.0"):
        """ 
            initialize the bot

            @param subreddit
                :type string
                :description: the name of the subreddit to get data from
        
            @param credential
                :type dict
                :description
                {
                  "client_secret":"#####",
                  "client_id":"###",
                  "username": "####",
                  "password":  "#####"
                }
            
            @param subreddit
                :type string
                :description: Reddit password

        """

        self.user_agent = "python:%s:v%s (by /u/%s)" % (APP_NAME, VERSION, credential["username"])
        self.__reddit = praw.Reddit(client_id=credential["client_id"], client_secret=credential["client_secret"],
                                  password=credential["password"], user_agent=self.user_agent,
                                  username=credential["username"])
        if subreddit is None:
            self.subreddit_tag = "not specified"
        else:
            self.subreddit_tag = subreddit
            self.subreddit = self.__reddit.subreddit(subreddit)

    def get_submissions(self):
        """
            get all submission ids in a subreddit.

            :rtype List
        """
        return list(set(comment.submission.id for comment in self.subreddit.comments()))

    def get_hot_submissions(self,sub_red=None, limit=10):
        """
            gets hot articles from the subreddit
            
            @param limit
                :type int
                :description: number of submissions to get

            :rtype generator
        """
        if sub_red is None:
            for submission in self.subreddit.hot(limit=limit):
                yield submission.id
        else:
            sub_reddit = self.__reddit.subreddit(sub_red)
            for submission in sub_reddit.hot(limit=limit):
                yield submission.id

    def get_submission(self, id):
        """
            @param id
                :type string
                :description: Reddit submission id

            rtype: Reddit.Submission
        """
        return self.__reddit.submission(id=id)

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
