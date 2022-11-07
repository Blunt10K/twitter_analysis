import tweepy
from os import environ,listdir
import json
from os.path import expanduser, join as osjoin
from utils import setup_api
import pandas as pd

def build_filename(number):
    
    return f'convos_{number}.json'

def existing_convos(path):
    
    df = pd.DataFrame()

    for f in listdir(path):
        file = osjoin(path,f)
        df = pd.concat((df,pd.read_json(file, orient='records')))
    
    return df['conversation_id'].unique()

def mentions():
    path = expanduser('~/spark_apps/unesco_mentions/')

    df_data = []
    for f in listdir(path):
        with open(osjoin(path,f),'r') as fp:
            df_data.extend(json.load(fp))

    df = pd.DataFrame(df_data)

    return df['conversation_id'].unique()


def most_recent(path):
    return max([int(i.strip('convos_.json')) for i in listdir(path)])


def collect():
    path = expanduser('~/spark_apps/convo_roots/')
    existing = existing_convos(path)
    ments = mentions()
    api = setup_api()
    

    tweet_fields = 'attachments,context_annotations,conversation_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source'
    user_fields = 'description,created_at,location,entities,public_metrics,verified'
    # expansions = 'geo.place_id,entities.mentions.username'
    place_fields = 'country,name'

    start = 0
    div = 1
    convos = pd.DataFrame()

    for i in range(100,len(ments), 100):
        d = api.get_tweets(list(ments[start:i]), tweet_fields=tweet_fields, user_fields=user_fields, place_fields = place_fields)
        start+= int(i/div)
        div += 1
        convos = pd.concat((convos, pd.DataFrame(d.data)))

    convos = convos[~convos['conversation_id'].isin(existing)]
    number = most_recent(path) + 1

    filename = osjoin(path,build_filename(number))

    convos.to_json(filename, orient = 'records')

