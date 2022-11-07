import tweepy
from os import listdir
import json
from os.path import expanduser, join as osjoin
from datetime import datetime as dt
from datetime import timedelta as td
from utils import setup_api

# def setup_api():
#     token = environ.get('BEARER_TOKEN')
#     return tweepy.Client(bearer_token = token,wait_on_rate_limit=True)

def build_filename(number):
    
    return f'recent_mentions{number}.json'

def most_recent(path):
    return max([int(i.strip('recent_mentions.json')) for i in listdir(path)])

def collect():
    user_id = 20646711
    path = expanduser('~/spark_apps/unesco_mentions/')
    number = most_recent(path)
    api = setup_api()

    tweet_fields = 'attachments,context_annotations,conversation_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source'
    user_fields = 'description,created_at,location,entities,public_metrics,verified'
    expansions = 'geo.place_id,entities.mentions.username'
    place_fields = 'country,name'
    start_time = dt.now() - td(hours = 6)


    for tweets in tweepy.Paginator(api.get_users_mentions, id = user_id, max_results = 100,expansions = expansions,
        user_fields = user_fields, tweet_fields = tweet_fields, place_fields = place_fields, start_time = start_time):

        number += 1
        data = [d.data for d in tweets.data]
        filename = osjoin(path,build_filename(number))
        with open(filename,'w') as fp:
            fp.write(json.dumps(data))
