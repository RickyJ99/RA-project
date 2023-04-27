def preprocess(raw_text):
    # regular expression keeping only letters
    letters_only_text = re.sub("[^a-zA-Z]", " ", raw_text)

    # convert to lower case and split into words -> convert string into list ( 'hello world' -> ['hello', 'world'])
    words = letters_only_text.lower().split()

    cleaned_words = []
    lemmatizer = (
        PorterStemmer()
    )  # plug in here any other stemmer or lemmatiser you want to try out

    # remove stopwords
    for word in words:
        if word not in stop_words:
            cleaned_words.append(word)

    # stemm or lemmatise words
    stemmed_words = []
    for word in cleaned_words:
        word = lemmatizer.stem(
            word
        )  # dont forget to change stem to lemmatize if you are using a lemmatizer
        stemmed_words.append(word)

    # converting list back to string
    return " ".join(stemmed_words)

speech_df = pd.read_csv("Full.csv", sep=",")
stop_words_file = "SmartStopList.txt"

stop_words = []

with open(stop_words_file, "r") as f:
    for line in f:
        stop_words.extend(line.split())

stop_words = stop_words


# preprocess(test_sentence)

"""you can see that "sentence" was stemmed to "sentenc", all stop words and punctuation were removed.
Let's apply that function to the incident texts in our speech dataframe
"""

speech_df["prep"] = speech_df["Main text"].apply(preprocess)

speech_df.head()

"""## Most Common Words
In order to get an idea about a dataset, it's useful to have a look at the most common words. Reading through all incident texts is cumbersome and inefficient. Let's extract the most common key words

"""


Counter(" ".join(speech_df["prep"]).split()).most_common(10)

# Commented out IPython magic to ensure Python compatibility.
# nice library to produce wordclouds


# if uising a Jupyter notebook, include:
# %matplotlib inline

all_words = ""

# looping through all incidents and joining them to one text, to extract most common words
for arg in speech_df["prep"]:
    tokens = arg.split()

    all_words += " ".join(tokens) + " "

wordcloud = WordCloud(
    width=700, height=700, background_color="white", min_font_size=10
).generate(all_words)

# plot the WordCloud image
plt.figure(figsize=(5, 5), facecolor=None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

plt.show()

from nltk.util import ngrams

n_gram = 2
n_gram_dic = dict(Counter(ngrams(all_words.split(), n_gram)))

for i in n_gram_dic:
    if n_gram_dic[i] >= 2:
        print(i, n_gram_dic[i])