import nltk
from textsim import remove_punctuation_map
from statistics import mean

UPPER_BOUND = 0.05
LOWER_BOUND = -0.05

class SentimentAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def find_sentence(text):
        """
            extract the sentences from the text

            :rtype str
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
        """
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
        """
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        nltk_sentiment = SentimentIntensityAnalyzer()
        score = nltk_sentiment.polarity_scores(sentence)['compound']

        return score


class CommentMetaAnalysis:
    """
        this class is used to calculate comment features
    """

    def __init__(self, comment):
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
    def quotedTextPerLength(self):
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
    def averageWordLength(self):
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
    def readingLevel(self):
        """
            calculates the reading ea
            :rtype float
        """
        if self._reading_level == None:
            from textstat.textstat import textstat
            self._reading_level = round(float(textstat.flesch_reading_ease(self._body)),4)

        return self._reading_level

