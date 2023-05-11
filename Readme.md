## Overview

This repository contains code and resources for a project that uses NLP AI to extract economic narratives. The repository is organized into several folders: `Code_From Download to Dataset`, `Data`, `Exploring_dataset`, and `Literature review`.

## `Code_From Download to Dataset`

This folder contains all the code and resources necessary to obtain four databases, including one that contains all speeches with their respective AI and UI indices. The following is a brief summary of each file:

- `1_Get_speech_dataset.ipynb`: This code downloads all speeches for the Trump and Biden administrations from the White House and saves them in `Data/dataset1_onlyrawdatadownloaded.csv`. It also saves a file called `url_speeches.txt` with all the links where it downloaded the speeches.

- `1_a_urlextraction.ipynb`: This file reads the file `url_speeches.txt` and returns the dataset. If you have a list of URLs from the White House and you want to download them, you can run this code.

- `2_extraction_info.ipynb`: This code uses NLP analysis to extract specific information from a speech, such as the location, time, speaker name, and date. It performs data cleaning, preprocessing, and feature extraction tasks using libraries such as `pandas`, `nltk`, `gensim`, and `spacy`.

- `3_cleaning_data.ipynb`: This code imports the `pandas` and `re` modules and reads a CSV file named `2_Data_after_infoextraolated.csv` using `pandas`' `read_csv()` function. It defines three functions to clean the text data, and then modifies the "Main text" column of the data frame by calling these functions. The modified data frame is saved to a new CSV file named `3_Data_after_cleaningdata.csv`.

- `4_AI_analysis.ipynb`: This code uses four BERT models to extract insightful information about narratives from the given dataframe:
    1. LatentDirichletAllocation model for topic extraction
    2. `heBERT_sentiment_analysis` for sentiment analysis that returns three indices reflecting the sentiment
    3. `en_core_web_lg` for thematic analysis to classify different narratives
    4. `heBERT_sentiment_analysis` with FED uncertainty for sentiment analysis.
    The output is saved in `Data/4_Data_with_AI_Market_Indicies.csv`.

## `Data`

This folder contains all the datasets saved after running the respective Python code. For example, dataset 3 is the output of the code 3 in the folder `Code_From Download to Dataset`.

## `Exploring_dataset`

This folder contains R code to get a quick view of the dataset and the properties of the time series.

## `Literature review`

This folder contains scientific articles that use a similar method and the citations for the AI models used in the project.
