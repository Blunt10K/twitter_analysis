import tweepy
from os import environ
from os.path import expanduser, join as osjoin
import json
import pandas as pd


def setup_api():
    token = environ.get('BEARER_TOKEN')
    
    return tweepy.Client(bearer_token = token,wait_on_rate_limit=True)


def build_filename(number):
    
    return f'followers_{number}.json'


user_id = 20646711
path = expanduser('~/spark_apps/twitter_followers/')
number = 0
api = setup_api()

user_fields = 'description,created_at,location,entities,public_metrics,verified'

for followers in tweepy.Paginator(api.get_users_followers,id = user_id,max_results = 1000, user_fields = user_fields):
    number += 1
    filename = osjoin(path,build_filename(number))
    df = pd.DataFrame(followers.data)
    with open(filename,'w') as fp:
        df.to_json(fp,orient='records')