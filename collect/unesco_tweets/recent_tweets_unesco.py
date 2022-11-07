import tweepy
from os import environ,listdir
import json
from os.path import expanduser, join as osjoin
from utils import setup_api



# def setup_api():
#     token = environ.get('BEARER_TOKEN')
#     return tweepy.Client(bearer_token = token,wait_on_rate_limit=True)

def build_filename(number):
    
    return f'recent_tweets{number}.json'

user_id = 20646711
path = expanduser('~/spark_apps/unesco_tweets2/')
number = 0
api = setup_api()

tweet_fields = 'attachments,context_annotations,conversation_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source'
user_fields = 'description,created_at,location,entities,public_metrics,verified'
place_fields = 'country,name'


for tweets in tweepy.Paginator(api.get_users_tweets, id = user_id, max_results = 100, exclude = ['retweets'],
    user_fields = user_fields, tweet_fields = tweet_fields, place_fields = place_fields):

    data = [d.data for d in tweets.data]
    filename = osjoin(path,build_filename(number))
    with open(filename,'w') as fp:
        fp.write(json.dumps(data))
    number += 1