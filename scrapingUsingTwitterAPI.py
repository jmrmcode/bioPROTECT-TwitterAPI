#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 17:05:59 2022

@author: juanmi
"""

import tweepy
import os
os.chdir("/home/juanmi/Documents/MariaZambrano/code")
import TWITTER_API_config
import time
import pandas as pd

# get tweets that include specific words
client = tweepy.Client(bearer_token= TWITTER_API_config.BEARER_TOKEN, wait_on_rate_limit = True)
query = 'zoonosis "and" biodiversity "and" loss -is:retweet'
response = client.search_recent_tweets(query = query, max_results = 10, tweet_fields = 'created_at', expansions = ['author_id'])

for tweet in response.data:
    print(tweet.id)

users = {u['id']: u for u in response.includes['users']}

"""
# get an user id
users = client.get_users(usernames = ['IUCN'])
for user in users:
    print(user)
"""
tweets_mode = "extended"
# get followers of an user    
users = client.get_users_followers(id = TWITTER_API_config.USER_ID2, user_fields = ['username'])# or name
for user in users.data:
    print(user.username) # or name

response = client.get_user(id = TWITTER_API_config.USER_ID2, user_fields = 'public_metrics')
response.data.public_metrics['followers_count']

###  getting tweets from an user account containing keywords or hashtags
limit = 1000
# note that the limit of tweets or whatever depends on the method we use
tweets = tweepy.Cursor(client.user_timeline, screen_name = TWITTER_API_config.USER_ID4, count = 200, 
         tweet_mode = "extended").items(limit)

# if "biodiversity" in tweets.text:  THIS IS INCOMPLETE

#########################################################################################
# Getting Tweet counts (volume) for a search query
# Replace with your own search query
query = '"infectious diseases" -is:retweet' # from:IUCN "biodiversity loss" "and" infectious "and" diseases  (zoonosis OR zoonoses OR zoonotic) "emerging infectious diseases"
# query2 = 'covid -is:retweet' # from:IUCN

# Replace with time period of your choice
start_time = '2006-04-01T00:00:00Z'

# Replace with time period of your choice
end_time = '2022-04-30T00:00:00Z'


limit = 1000000
for cc in tweepy.Paginator(client.get_all_tweets_count, query=query, granularity='day', start_time = start_time, end_time = end_time).flatten(limit):
    print(cc.get('tweet_count'))


# work with lists and dictionarys
len(cc.data) # counts.data is a list
counts.data[0] # this is a dictionary
counts.data[0].keys()
counts.data[0].get('end')

for cc in counts:
    print(counts.data)


# maxTweets = 10
counts2 = []
for i,countt in enumerate(tweepy.Paginator(client.get_all_tweets_count,
                                 query = query,
                                 granularity = 'day',
                                 start_time = start_time,
                                 end_time = end_time).flatten(limit)):
    #if i > maxTweets:
     #   break
    print(i)
    start = countt.get('start')
    end = countt.get('end')
    count = countt.get('tweet_count')
    counts2.append({
        "start": start,
        "end": end,
        "count": count     
    })

counts_df = pd.DataFrame(counts2)
counts_df.head()    
counts_df.tail()

# convert dates
# counts_df2 = pd.DataFrame(columns=["start","end","count"], index=[str(i) for i in range(0, counts_df.shape[0])])
for i in range(0, 2):
    for j in range(0, counts_df.shape[0]):
        ts = time.strptime(counts_df.iloc[j,i][:7], "%Y-%m") # time.strptime(counts_df.iloc[j,i][:10], "%Y-%m-%d")
        tt = time.strftime("%Y-%m", ts) # time.strftime("%Y-%m-%d", ts)
        counts_df.iloc[j,i] = tt

df2 = counts_df.sort_values(by="start")
df2.head()
df2.tail()
df2 = df2.groupby('start').sum()
df2.reset_index(inplace=True)
# df2["start"] = pd.to_datetime(df2["start"])
#df2.to_csv('/home/juanmi/Documents/MariaZambrano/data/tweetsCountApr06Apr22EmInfdis.csv', encoding='utf-8')
df2 = pd.read_csv ('/home/juanmi/Documents/MariaZambrano/data/tweetsCountApr06Apr22EmInfdis.csv')


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(df2["start"], df2["count"], width=0.5, color = 'gray')
fig.autofmt_xdate()
ax.set_title('Tweets containing the words: BIODIVERSITY & LOSS & INFECTIOUS & DESEASES')
ax.set_xlabel('Date')
ax.set_ylabel('Count of tweets')
ax.title.set_size(17)
ax.yaxis.label.set_size(16)
ax.xaxis.label.set_size(15)
# ax.set_xticklabels(df2["start"])


# PLOT RATE OF TWEETS PER YEAR
# sum by year the above df
df3 = pd.read_csv ('/home/juanmi/Documents/MariaZambrano/data/tweetsCountApr06Apr22EmInfdis.csv')
df2["start"] = pd.to_datetime(df2["start"])
df4 = df2.groupby(df2['start'].dt.year)['count'].agg(['sum'])

# sum by year a loaded data frame
df3 = pd.read_csv ('/home/juanmi/Documents/MariaZambrano/data/tweetsCountApr06Apr22EmInfdisBioLoss.csv')
df3["start"] = pd.to_datetime(df3["start"])
df5 = df3.groupby(df3['start'].dt.year)['count'].agg(['sum'])
# percentages of tweets
perc_tweets = pd.DataFrame(columns=["date","percentage"], index=[str(i) for i in range(0, df4.shape[0])])
perc_tweets.reset_index(inplace=True)
for i in perc_tweets.index:
    if df4.iloc[i,0] == 0:
        perc_tweets.iloc[i,2] = 0 
    else:
        perc_tweets.iloc[i,2] = (df5.iloc[i,0] * 100) / df4.iloc[i,0]
    perc_tweets.iloc[i,1] = df5.index[i]

perc_tweets["date"] = pd.to_datetime(perc_tweets['date'], format='%Y')

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(perc_tweets["date"], perc_tweets["percentage"], width=150, color = 'gray')
#fig.autofmt_xdate()
ax.set_title('Rate of Tweets that mention biodiversity loss in Tweets that talk about infectious diseases')
ax.set_xlabel('Date')
ax.set_ylabel('Rate of tweets in %')
ax.title.set_size(15)
ax.yaxis.label.set_size(16)
ax.xaxis.label.set_size(15)
#ax.xaxis.set_major_locator(mdates.YearLocator())
ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_xticks(perc_tweets["date"])
#fig.savefig("test.svg")


#####################################################################################
# Getting Tweets from the full-archive of public Tweets for a specific time-frame
# source: https://docs.google.com/document/d/1ibIah7ef81e_FLA82rESScmnd8Uj4f2iwCh4XYhmJX4/edit

# Replace with your own search query
query = 'biodiversity "and" loss "and" infectious "and" diseases -is:retweet' # from:IUCN
# Replace with time period of your choice
start_time = '2020-03-01T00:00:00Z'

# Replace with time period of your choice
end_time = '2022-04-30T00:00:00Z'

# Replace the limit=1000 with the maximum number of Tweets you want
for tweet in tweepy.Paginator(client.search_all_tweets, query=query,
             tweet_fields=['context_annotations', 'created_at'], 
             start_time=start_time, end_time=end_time, max_results=100).flatten(limit=10):
    print(tweet.id)
