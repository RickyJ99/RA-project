# Extractiondatafromurl

import pandas as pd
import warnings
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from datetime import datetime
import re
import nltk
from collections import Counter
import gensim

nltk.download("wordnet")
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer

warnings.filterwarnings("ignore")


def extr(url, adm):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    if adm == 1:  # biden administration
        # get metas
        # extract title
        title = soup.find("meta", property="og:title")
        title = title["content"]
        print("Title:" + title)

        # extract description
        desc = soup.find("meta", property="og:description")
        desc = desc["content"]
        print("Description:" + desc)

        # extract datatime
        date = soup.find("meta", property="article:published_time")
        date_str = str(date["content"])

        # convert the date in the correct format
        date = datetime.fromisoformat(date_str)
        print("Date:" + str(date))

        # extract text
        body = soup.find("section", class_="body-content")
        body = body.text
        print("Text extracted")
    elif adm == 0:
        # extract title
        title = soup.find("h1", {"class": "page-header__title"}).text
        print("Title:" + title)

        # extract date
        date_str = soup.find("time").text

        # convert the date in the correct format
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        date = date_obj.isoformat() + "+00:00"
        print("Date:" + str(date))

        # no desc with the trump

        # extract text
        body = soup.find("div", class_="page-content__content editor")
        body = body.text
        print("Text extracted")

        # extract description using library gensim
        desc = "Nan"

    print("----------------------------------------------------")
    print("----------------------------------------------------")
    out = [date, title, desc, body, url]
    return out
