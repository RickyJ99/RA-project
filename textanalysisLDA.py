import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer
import pandas as pd
import re as re
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Step 1: Preprocessing
def preprocess(text):
    # regular expression keeping only letters
    letters_only_text = re.sub("[^a-zA-Z]", " ", text)

    # Remove punctuation and lowercase all characters
    text = letters_only_text.translate(
        str.maketrans("", "", string.punctuation)
    ).lower()

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]

    # Remove " '
    stop_words_file = "SmartStopList.txt"

    stop_words = []

    with open(stop_words_file, "r") as f:
        for line in f:
            stop_words.extend(line.split())

    stop_words = stop_words
    tokens = [token for token in tokens if token not in stop_words]
    # Perform lemmatization
    lemmatizer = WordNetLemmatizer()  # WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return tokens


# Step 2: Create a document-term matrix
def create_document_term_matrix(documents):
    # Initialize a CountVectorizer object
    vectorizer = CountVectorizer(tokenizer=preprocess)

    # Fit and transform the documents into a document-term matrix
    document_term_matrix = vectorizer.fit_transform(documents)

    return document_term_matrix, vectorizer.get_feature_names_out()


# Step 3: Run LDA
def run_lda(document_term_matrix, n_topics):
    # Initialize an LDA object
    lda = LatentDirichletAllocation(n_components=n_topics)

    # Fit the LDA model to the document-term matrix
    lda.fit(document_term_matrix)

    return lda


# Step 4: Analyze the results
def analyze_results(lda, feature_names, n_top_words):
    # Print the top words for each topic
    for topic_idx, topic in enumerate(lda.components_):
        print("Topic #%d:" % topic_idx)
        print(
            " ".join(
                [feature_names[i] for i in topic.argsort()[: -n_top_words - 1 : -1]]
            )
        )


# step 5 generate a word cloud
def create_word_clouds(lda, feature_names, n_top_words):
    # Create a WordCloud object
    wordcloud = WordCloud(background_color="white")

    # Generate a word cloud for each topic
    for topic_idx, topic in enumerate(lda.components_):
        # Get the top words for the current topic
        top_words = [feature_names[i] for i in topic.argsort()[: -n_top_words - 1 : -1]]

        # Generate the word cloud
        wordcloud.generate_from_text(" ".join(top_words))

        # Display the word cloud
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Topic #{topic_idx}")

        # Save the figure to a file
        plt.savefig(f"wordcloud/topic_{topic_idx}.png", bbox_inches="tight")


df = pd.read_csv("Extraction.csv", sep=",")
"""documents = df[
    (df["Date Time"].str.contains("2020"))
    & (df["Title"].str.contains("Press Bri"))
    & (
        df["Title"].str.contains("Trump")
        | df["Title"].str.contains("trump")
        | df["Title"].str.contains("President")
        | df["Speaker"].str.contains("president")
    )
].loc[:, "Main text"]
"""

documents = df[(df["Date Time"].str.contains("2020"))].loc[:, "Main text"]
# Preprocess the documents and create a document-term matrix
document_term_matrix, feature_names = create_document_term_matrix(documents)

# Run LDA on the document-term matrix with 2 topics
lda = run_lda(document_term_matrix, 5)

# Analyze the results and print the top 5 words for each topic
analyze_results(lda, feature_names, 20)

# This will create and display a word cloud for each topic using the top 5 words.
create_word_clouds(lda, feature_names, 20)
