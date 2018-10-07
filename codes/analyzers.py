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
        """
        # text = text.replace('\n', '')
        # pattern = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
        # result = pattern.findall(text)
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
            returns the mean score for all the sentences in 
            a comment.
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
        if self._length == None:
            self._length = len(self._body)
        return self._length

    @property
    def quotedTextPerLength(self):
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

            self._quoted_text_per_length = round(count/self._length, 4)

        return self._quoted_text_per_length

    @property
    def averageWordLength(self):

        if self._average_word_length == None:
            from statistics import mean
            from collections import defaultdict

            tokenDict = defaultdict(int)
            tokens = nltk.word_tokenize(
                self._body.lower().translate(remove_punctuation_map))

            for token in tokens:
                tokenDict[token] += len(token)

            self._average_word_length = mean(tokenDict.values())

        return round(self._average_word_length, 3)

    @property
    def readingLevel(self):
        if self._reading_level == None:
            from textstat.textstat import textstat
            self._reading_level = textstat.flesch_kincaid_grade(self._body)

        return self._reading_level

