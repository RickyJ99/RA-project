# Data Analysis of Trump Tweets
# Nathan Taback
# https://utstat.toronto.edu/~nathan/teaching/sta4002/Class4/trumptweets-students.html

#Library

library(jsonlite)
library(tidyverse)
library(stringr)
library(lubridate)
library(scales)
library(tidytext)

# Data

url <- "http://utstat.toronto.edu/~nathan/teaching/sta4002/Class4/trumptweets.JSON"
trumptweets <- fromJSON(url)
tweets <- trumptweets %>% select(source, text, created_at,id_str) %>% 
  mutate(created_at = parse_date_time(created_at, "a b! d! H!:M!:S! z!* Y!")) %>% 
  filter(created_at < "2017-03-26") %>%
  mutate(source=ifelse(str_detect(source,"iPhone"),"iPhone",
  ifelse(str_detect(source,"Android"),"Android","NA"))) %>%
  filter(source %in% c("iPhone", "Android"))

# Exploring the data

tweets %>% count(source, hour = hour(with_tz(created_at, "EST"))) %>%
  mutate(percent = n / sum(n)) %>%
  ggplot(aes(hour, percent, color = source)) +
  geom_line() +
  scale_y_continuous(labels = percent_format()) +
  labs(x = "Hour of day (EST)",
       y = "% of tweets",
       color = "")

tweet_picture_counts <- tweets %>% filter(!str_detect(text, '^"')) 
%>% count(source, picture = ifelse(str_detect(text, "t.co"), "Picture/link", "No picture/link"))

ggplot(tweet_picture_counts, aes(source, n, fill = picture)) +
 geom_bar(stat = "identity", position = "dodge") + 
 labs(x = "", y = "Number of tweets", fill = "")

#Comparison words

reg <- "([^A-Za-z\\d#@']|'(?![A-Za-z\\d#@]))"

tweet_words <- tweets %>% filter(created_at < "2017-03-26") %>% 
filter(!str_detect(text, '^"')) %>% mutate(text = str_replace_all(text,
 "https://t.co/[A-Za-z\\d]+|&amp;", "")) %>% unnest_tokens(word, text, 
 token = "regex", pattern = reg) %>% filter(!word %in% stop_words$word,
  str_detect(word, "[a-z]"))

head(tweet_words)

tweet_words %>% count(word) %>% top_n(50) %>% ggplot(aes(word,n))+
geom_col()+coord_flip()+labs(x="Word",y="Number of times word ocurres in a Tweet")

tweet_words %>% count(word) %>% mutate(word=reorder(word,n)) %>% 
top_n(20) %>% ggplot(aes(word,n))+geom_col()+coord_flip()+
labs(x="Word",y="Number of times word ocurres in a Tweet")

# Sentiment analysis
sentiments %>% filter(lexicon=="nrc") %>% filter(word=="abandon") %>% select(-score) %>% head()


nrc <- sentiments %>%
  filter(lexicon == "nrc") %>%
  dplyr::select(word, sentiment)

sources <- tweet_words %>%
  group_by(source) %>%
  mutate(total_words = n()) %>%
  ungroup() %>%
  distinct(id_str, source, total_words)

by_source_sentiment <- tweet_words %>%
  inner_join(nrc, by = "word") %>%
  count(sentiment, id_str) %>%
  ungroup() %>%
  complete(sentiment, id_str, fill = list(n = 0)) %>%
  inner_join(sources) %>%
  group_by(source, sentiment, total_words) %>%
  summarize(words = sum(n)) %>%
  ungroup()

head(by_source_sentiment)