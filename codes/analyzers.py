# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to calculate new feature for graph nodes

import nltk
from textsim import remove_punctuation_map
from statistics import mean

class SentimentAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def find_sentence(text):
        """
            extract the sentences from the text
            @param text
                :type string
                :description:
            
            :rtype string
        """
        text = text.lower()
        result = nltk.sent_tokenize(text)
        result = result if len(result) > 0 else text
        return result
   
    @staticmethod
    def convert_score(score):
        """
            convert the score to a word
            Positive for scores >= 0.05
            Negative for scores <= -0.05
            Neutral for scores that fall in between

            @param score
                :type int
                :description: sentiment score
        """
        UPPER_BOUND = 0.05
        LOWER_BOUND = -0.05

        if score is None:
            return None
        elif score >= UPPER_BOUND:
            return "Positive"
        elif score <= LOWER_BOUND:
            return "Negative"
        else:
            return "Neutral"

    @staticmethod
    def add_sentiment(comment):
        """
            calculates the mean score for all the sentences in 
            a comment.
            
            @param comment
                :type CommentNode
                :description: a comment node class object
            
            :rtype float
        """
        sentences = SentimentAnalysis.find_sentence(comment.body)
        scores = [SentimentAnalysis.sentiment(
            sentence) for sentence in sentences]

        return round(mean(scores), 4) if len(scores) > 0 else None

    @staticmethod
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

            @param sentence
                :type string
                :description: sentence to analyze

            :rtype: float
        """
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        nltk_sentiment = SentimentIntensityAnalyzer()
        score = nltk_sentiment.polarity_scores(sentence)['compound']

        return score


class CommentAnalysis:
    """
        this class is used to calculate comment features

        Attributes
        ----------
        length: number of characters in the comment

        quoted_text_per_length: quoted texts divided by the length of comment

        average_word_length: number of words divided by the sum of the length of
                             words in the comment

        reading_level: the reading ease of the comment

    """

    def __init__(self, comment):
        """
            Builds the object

            @param comment
                :type CommentNode
                :description: comment node class object
        """
        self._body = comment.body
        self._length = None
        self._quoted_text_per_length = None
        self._average_word_length = None
        self._reading_level = None

    @property
    def length(self):
        """
            gets the norm of the comment vector

            :rtype int
        """
        if self._length == None:
            self._length = len(self._body)
        return self._length

    @property
    def quoted_text_per_length(self):
        """
            calculates the amount of quoted text per length of comment

            :rtype float
        """
        stack = list()
        count = 0
        startCounting = False
        if self._quoted_text_per_length == None:
            for c in self._body:
                if(startCounting):
                    count += 1

                if c == '\"':
                    stack.append(c)
                    startCounting = True

                if(len(stack) == 2):
                    startCounting = False
                    del stack[:]

            self._quoted_text_per_length = float(round(count/self._length, 4))

        return self._quoted_text_per_length

    @property
    def average_word_length(self):
        """
            calculates the average word length of a comment
            :rtype float
        """

        if self._average_word_length == None:
            from statistics import mean
            from collections import defaultdict

            tokenDict = defaultdict(int)
            tokens = nltk.word_tokenize(
                self._body.lower().translate(remove_punctuation_map))

            for token in tokens:
                tokenDict[token] += len(token)

            self._average_word_length = float(round(mean(tokenDict.values()),3))

        return self._average_word_length

    @property
    def reading_level(self):
        """
            calculates the reading ea
            :rtype float
        """
        if self._reading_level == None:
            from textstat.textstat import textstat
            self._reading_level = round(float(textstat.flesch_reading_ease(self._body)),4)

        return self._reading_level

