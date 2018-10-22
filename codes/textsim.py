import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]


def normalize(text):
    '''
        remove punctuation, lowercase, stem
    '''
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
def cosine_sim(doc_0, doc_1):
    """
        calculates the cosine similarity of the two documents

        :rtype float :range [0,1]
    """
    tfidf = vectorizer.fit_transform([doc_0, doc_1])
    return ((tfidf * tfidf.T).A)[0,1]


