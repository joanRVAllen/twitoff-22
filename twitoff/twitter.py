from os import getenv
import tweepy # interacts with Twitter
import spacy # vectorizes tweets
from .models import DB, Tweet, User


# connect to Twitter API
TWITTER_API_KEY = getenv('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = getenv('TWITTER_API_KEY_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)

# not sure what this does
nlp = spacy.load('my_model')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector

def add_or_update_user(username):
    try:
        twitter_user = TWITTER.get_user(username)

        # If they exist then update that user, if we get something back
        # then instantiate a new user
        db_user = (User.query.get(twitter_user.id)) or User(
            id=twitter_user.id, name=username)
        
        DB.session.add(db_user)

        tweets = twitter_user.timeline(
            count=200,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="Extended"
        ) # list of tweets from 'username'

        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        for tweet in tweets:
            vectorized_tweet = vectorize_tweet(tweet.text)
            db_tweet = Tweet(id=tweet.id, text=tweet.text,
                            vect=vectorized_tweet)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    except Exception as e:
        print('Error processing {}: {}'.format(username, e))

    else:
        DB.session.commit()