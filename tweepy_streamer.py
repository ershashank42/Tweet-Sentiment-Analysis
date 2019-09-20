from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
#This is a class that will allow us to listen to the tweets kind of the firehose of tweets as they come based on certain
#keywords or hashtags
from tweepy import OAuthHandler
#module for authentication based on the credentials that we stored in the other file associated with the twitter app
from tweepy import Stream
#import twitter_credentials

import twitter_credentials
from textblob import TextBlob

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

class TwitterClient():
    def __init__(self,twitter_user=None):   #replace None with specific user to get their tweets
        self.auth = TwitterAuthenicator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user    #if u want to get tweets from another user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self,num_tweets):    #funtion that allows us to get tweets
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):   #get specific user
        #timeline tweets if u don't define a user specifically, it defines to you by default and it will get your
        #timeline tweets and .items() will tell how many tweets to actually get from timeline
            tweets.append(tweet)
        return tweets

    def get_friend_list(self,num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends,id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline,id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

class TwitterAuthenicator():
    def authenticate_twitter_app(self):
        auth=OAuthHandler(twitter_credentials.CONSUMER_KEY,twitter_credentials.CONSUMER_SECRET)     #authentication
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN,twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth
class TwitterStreamer():    #class for streaming and processing live tweets
    def __init__(self):
        self.Twitter_authenicator = TwitterAuthenicator()
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
        #this handles twitter authentication and connection to twitter streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.Twitter_authenicator.authenticate_twitter_app()
        stream = Stream(auth,listener) #we now filter the tweets based on some keywords or hashtags because while
        #streaming there will be a lot of tweets that gets streamed a same time.
        stream.filter(track=['narendra modi','donald trump']) #this will add all the tweets that have the keywords defined in list.

#create a basic class which will allow to print the tweets to stdout.
class TwitterListener(StreamListener):   #basic class that prints tweets to stdout
    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets_filename,'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("error on data: %s" % str(e))
        return True

    def on_error(self,status):
        if status == 420:
            return False    #returns False on_data method in case rate limit occurs.
        print(status)

'''on_data is a method which will take in the data that is streamed in from the listener and is printing the data that we get
and returns that everything went well i.e. True value.
on_error happens when some error occurs which we are overriding and printing the error which is passed through status variable
and we're printing it on screen. if any error occurs, this method will be triggered and it is displayed on screen.'''

#create another class that will be responsible for analyzing the tweets that we extract from twitter
class TweetAnalyzer():
    #funtionality for analyzing and categorizing contents from tweets.

    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+) | ([^0-9A-Za-z \t]) | (\w+:\/\/\S+)"," ",tweet).split())
        #regex removes special characters from the string and then we're moving hyperlinks and returning the result of clean tweet.

    #function to call textblob for sentiment analysis of the tweet and returning the sentiment
    def analyze_sentiment(self,tweet):
        #create an object that will be returned to us from textblob
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:      #polarity-metric that decide the sentiment of tweet
            return 1        #interprets the tweetas positive
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self,tweets):
        #create a dataframe object to store the tweet info into dataframe
        df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['tweets'])    #self-explainatory
        #inbuilt function of pandas that allows to create dataframe based on the content that we feed to it
        df['id'] = np.array([tweet.id for tweet in tweets])
        #creates a column name 'id' and store the id of each tweet in tweets list
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


#we now create an object for the class and get on to streaming the tweets. this is the main part of the program.
if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    #api is the variable that has twitter client object that we created in that class
    tweets = api.user_timeline(screen_name="be1iev3r",count=20)
    #we can use user_timeline function for specifying the user from which we extract the tweets and
    #how many no. of tweets we want to extract

    #print(dir(tweets[0]))   #this will tell us what type of pieces of info we can extract from a tweet.
    #it displays list of all possible things that can be extracted from a tweet. eg. text,username, tweetID, likeCount etc.
    #print(tweets[0].id)     #prints id of the first tweet in the tweets list

    df = tweet_analyzer.tweets_to_data_frame(tweets)
    '''we created an object to stream the tweets from the client and we store it into a dataframe'''
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    print(df)

    
