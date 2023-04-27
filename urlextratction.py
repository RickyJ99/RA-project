import pandas as pd
import warnings
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from datetime import datetime
import re

from collections import Counter

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
warnings.filterwarnings("ignore")
"""# Download the data from the white house 
Importing all the links from https://www.whitehouse.gov/briefing-room/press-briefings/ 
"""

base_url = "https://www.whitehouse.gov/briefing-room/press-briefings/page/"
page_number = 1
all_links = []
# Biden administration
while True:
    try:
        url = base_url + str(page_number)
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features="html.parser")
        urls = soup.find_all("a", class_="news-item__title")
        for url in urls:
            all_links.append(url["href"])
        page_number += 1
    except HTTPError:
        break

# Trump administration
base_url = "https://trumpwhitehouse.archives.gov/briefings-statements/page/"
page_number = 1

while True:
    try:
        url = base_url + str(page_number)
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features="html.parser")
        urls = soup.find_all("h2", class_="briefing-statement__title")
        for url in urls:
            all_links.append(url.a["href"])
        page_number += 1
    except HTTPError:
        break

with open("url.txt", "w") as f:
    for link in all_links:
        f.write(link + "\n")

"""

1.   Reading the text file with the links
2.   Recall the extrapolation function for each link
3.   Saving the data in a csv file

"""

# reading the file with the link
f = open("url.txt", "r")
url1 = f.readlines()


# print(speech_text)
# create a data frame
# initialize variables
date = []
title = []
desc = []
speech_text = []
link = []
admin = []

# download the data
for url_count in url1:
    print("Analizing:" + url_count)
    if "https://www.whitehouse.gov/" in url_count:  # biden adm
        out = extr(str(url_count), 1)  # recalling function extrapolation
        admin.append("Biden")
    elif "https://trumpwhitehouse.archives.gov/" in url_count:
        out = extr(str(url_count), 0)  # recalling function extrapolation
        admin.append("Trump")

    # append the results
    date.append(out[0])
    title.append(out[1])
    desc.append(out[2])
    speech_text.append(out[3])
    link.append(out[4])

columns_name = [
    "Administration",
    "Date Time",
    "Title",
    "Description",
    "Main text",
    "URL",
]

df_imported = pd.DataFrame(
    list(zip(admin, date, title, desc, speech_text, link)), columns=columns_name
)


# save in a csv file
df_imported.to_csv("Full.csv", index=False)
# """Thus I save a csv fil called Book1.csv. Now I open and import the data and starting the text analysis """
