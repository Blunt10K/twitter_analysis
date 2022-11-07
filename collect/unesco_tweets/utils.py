import tweepy
from os import environ



def setup_api():
    token = environ.get('BEARER_TOKEN')
    return tweepy.Client(bearer_token = token,wait_on_rate_limit=True)