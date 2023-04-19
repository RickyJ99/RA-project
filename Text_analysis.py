# Importing necessary library
import pandas as pd
import numpy as np
import nltk
import os
import nltk.corpus  # sample text for performing tokenization

text = "In Brazil they drive on the right-hand side of the road. Brazil has a large coastline on the eastern side of South America"  # importing word_tokenize from nltk


from nltk.tokenize import (
    word_tokenize,
)  # Passing the string text into word tokenize for breaking the sentences

token = word_tokenize(text)
token

# finding the frequency distinct in the tokens
# Importing FreqDist library from nltk and passing token into FreqDist
from nltk.probability import FreqDist

fdist = FreqDist(token)
fdist
