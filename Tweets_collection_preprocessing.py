#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 17:05:59 2022

@author: Juan M. Requena-Mullor
"""

## load modules
## the required modules are supposed to be already installed
import tweepy
import os
os.chdir("~/type the path to your API credentials")
import TWITTER_API_config
import time
import pandas as pd
import numpy as np
import re
from textblob import Word

############################################################################################################################################################################
###############                              TWEETS COLLECTION                            ##################################################################################
# Twitter API v2 Client
client = tweepy.Client(bearer_token= TWITTER_API_config.BEARER_TOKEN, wait_on_rate_limit = True)
# define the query
query = '#onehealth -is:retweet lang:en'

# create the period to collect tweets
start_time = '2006-04-01T00:00:00Z'
end_time = '2022-12-31T00:00:00Z'

# collect tweets
counts2 = []
i = 0
for countt in tweepy.Paginator(client.search_all_tweets,
                                 query = query,
                                 max_results = 100, start_time=start_time, end_time=end_time,
                                 tweet_fields = ['context_annotations','created_at','public_metrics'],
                                 expansions = ['geo.place_id','author_id','entities.mentions.username','in_reply_to_user_id','referenced_tweets.id.author_id'],
                                 user_fields = ['name','username','location','verified','public_metrics'],
                                 place_fields = ['country','country_code']).flatten():
    retweet_count = countt.public_metrics['retweet_count']
    reply_count = countt.public_metrics['reply_count']
    like_count = countt.public_metrics['like_count']
    text = countt.text
    created_at = countt.created_at
    author_id = countt.author_id
    tweet_id = countt.id
    counts2.append({
        "tweet_id": tweet_id,
        "author_id": author_id,
        "text": text,
        "created_at": created_at,
        "retweet_count": retweet_count,
        "reply_count": reply_count,
        "like_count": like_count
    })
    i = i + 1
    print(i)
    time.sleep(1)

# transform the output into a data frame
counts_df = pd.DataFrame(counts2)

########################################################################################################################################################################################
################                         DATA PRE-PROCESSING                        ####################################################################################################
# define words to discard
stopwords = ["for", "on", "an", "a", "of", "and", "in", "the", "to", "from", "by", "at"]
personal_pronouns = ["i", "you", "she", "he", "it", "we", "they", "me", "us", "them", "her", "him", "yours", "my", "mine", "its", "our","those","these","your","their"]
others = ["is", "are", "dr", "will", "would", "amp", "this", "that", "amr", "be", "but", "with", "while", "must","one","health","about","can","just","being","where","not","yes","also","g","why","across","between","many","may","what","animal","human","approach","see",
"so","therefore","finds","represented","multi","through","more","less","great","was","were","did","do","how","as","has","have","had","some","any","who","whom","new","today","all","into","which","first","second","too","take","diseases","most","better",
"here","well","could","use","via","need","now","good","should","week","only","other","when","using","every","types","before","dog","there","been",
"two","based","during","back","high","much","best","such","get","make","around","taken","attached","says","every","day","drug"]

# define the cleaning function
def clean_tweet(tweet):
    if type(tweet) == np.cfloat:
        return ""
    temp = tweet.lower()
    temp = re.sub("'s", "", temp) # to avoid removing contractions in english
    temp = re.sub("@[A-Za-z0-9_]+","", temp) # Removing mentions
    temp = re.sub("#+","", temp) # Removing hashtags
    temp = re.sub(r'http\S+', '', temp) # Removing links
    temp = re.sub(r"www.\S+", "", temp) # Removing links
    temp = re.sub('[()!?]', ' ', temp) # Removing punctuations
    temp = re.sub('\[.*?\]',' ', temp) # Removing punctuations
    temp = re.sub("[^a-z0-9]"," ", temp) # Filtering non-alphanumeric characters
    temp = re.sub(r"[0-9]", "", temp) # Removing numbers
    temp = re.sub(r"\n", "",temp) # Removing line or tab character (\n, \r, \t..)
    temp = temp.split() # Tokenization = tokenize your text into tokens (ie, smaller components)
    temp = [w for w in temp if not w in stopwords] # Stop words removal
    temp = [w for w in temp if not w in personal_pronouns]  # Stop words removal
    temp = [w for w in temp if not w in others] # other words removal
    temp = [w for w in temp if len(w)>2] # remove isolated letters
    temp = [w for w in temp if Word(w).spellcheck()[0][1]==1 or w=='onehealth'] # remove misspellings and/or typos, except for onehealth
    temp = " ".join(word for word in temp)
    return temp.split()

# cleaning loop. This may take several hours to run
results = [clean_tweet(tw) for tw in counts_df.text]
ff = pd.DataFrame(np.array(results, dtype=object))
results = ff.squeeze()