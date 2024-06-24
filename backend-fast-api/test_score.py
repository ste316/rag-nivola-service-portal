import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample documents
docs = ["This is a sample document.", "Another sample document with similar text."]

# Create a TF-IDF vectorizer
vectorizer = TfidfVectorizer()


# --------------------------------------------------------------------------------------------


text = """Hello, this is the first sentence. This is the second. 
And this may or may not be the third. Am I right? No? lol..."""

import re
s = re.split(r'[.?!:]+', text)
print(s)
def search(word, sentences):
       return [i for i in sentences if re.search(r'\b%s\b' % word, i)]

aas = search('is', s)


print(aas)