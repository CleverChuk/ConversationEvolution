# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to calculate the similarity between 
#          two strings
from nltk import stem, word_tokenize 
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

def normalize(text):
    '''
        remove punctuation, lowercase, stem
       
        @param text
            :type string
            :description: text
    '''
    return stem_tokens(word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
def cosine_sim(doc_0, doc_1):
    """
        calculates the cosine similarity of the two documents

        @param doc_0
            :type string
            :description: first document 

        @param doc_1
            :type string
            :description: second document
        
        :rtype float :range [0,1]
    """
    tfidf = vectorizer.fit_transform([doc_0, doc_1])
    return ((tfidf * tfidf.T).A)[0,1]


