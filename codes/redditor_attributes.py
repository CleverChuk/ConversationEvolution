"""Info for a Redditor
==================================== ======================================
    Attribute                            Description
    ==================================== ======================================
    ``comment_karma``                    The comment karma for the Redditor.
    ``comments``                         Provide an instance of
                                         :class:`.SubListing` for comment
                                         access.
    ``created_utc``                      Time the account was created,
                                         represented in `Unix Time`_.
    ``has_verified_email``               Whether or not the Redditor has
                                         verified their email.
    ``icon_img``                         The url of the Redditors' avatar.
    ``id``                               The ID of the Redditor.
    ``is_employee``                      Whether or not the Redditor is a
                                         Reddit employee.
    ``is_friend``                        Whether or not the Redditor is friends
                                         with the authenticated client.
    ``is_gold``                          Whether or not the Redditor has active
                                         gold status.
    ``link_karma``                       The link karma for the Redditor.
    ``name``                             The Redditor's username.
    ``subreddit``                        If the Redditor has created a
                                         user-subreddit, provides a dictionary
                                         of additional attributes. See below.
    ``subreddit['banner_img']``          The url of the user-subreddit banner.
    ``subreddit['name']``                The name of the user-subreddit
                                         (prefixed with 't5').
    ``subreddit['over_18']``             Whether or not the user-subreddit is
                                         NSFW.
    ``subreddit['public_description']``  The public description of the user-
                                         subreddit.
    ``subreddit['subscribers']``         The number of users subscribed to the
                                         user-subreddit.
    ``subreddit['title']``               The title of the user-subreddit.
    ==================================== ======================================
"""