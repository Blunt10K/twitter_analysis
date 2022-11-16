import streamlit as st
from datetime import datetime as dt
from datetime import timedelta as td
from engagement_utils import *
from graphs import *
from google.oauth2 import service_account
from gsheetsdb import connect
from places_utils import *
from following_utils import *
from sentiment_utils import *
import pytz

st.set_page_config(page_title='UNESCO Twitter presence',layout='wide')


@st.experimental_singleton()
def connect_sheets():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    return connect(credentials=credentials)


@st.experimental_memo(ttl=3600,show_spinner=True)
def load_data(_conn):
    engagement = preprocess_engagement(_conn, st.secrets['unes_tweets_url'])
    baseline = engagement.mean(numeric_only=True).round(1)
    engagement = engagement.groupby('created_at',as_index=False).sum()

    hashtags = preprocess_hashtags(_conn, st.secrets['tweets_url'])

    places = preprocess_places(_conn, st.secrets['places_url'])

    places = preprocess_following(_conn, st.secrets['following_url'], places)

    fos = preprocess_fo(_conn, st.secrets['fo_url'])

    mentions, convo_sentiment = preprocess_sentiment(_conn, st.secrets['ment_url'],st.secrets['roots_url'])

    return engagement, hashtags, baseline, places, fos, mentions, convo_sentiment

conn = connect_sheets()

engage, hashtags, baseline, places, fos, mentions, convo_sentiment = load_data(conn)
engagement, following, sentiment = st.tabs(['Engagement', 'Following','Sentiment'])

# st.session_state['start_date'] = analysis['created_at'].min()
# st.session_state['end_date'] = analysis['created_at'].max()

# with st.sidebar:
#     st.header("Engagement over the following period")
#     start = st.date_input("Start",min(analysis['created_at']),min(analysis['created_at']),max(analysis['created_at']))
#     end = st.date_input("End",max(analysis['created_at']),start + td(days=1),max(analysis['created_at']))
    

with engagement:
    st.header('Engagement with UNESCO from:')
    start_date, end_date = st.columns(2)

    start = start_date.date_input("Start",min(engage['created_at']),min(engage['created_at']),
            max(engage['created_at']),key='start_date')
    end = end_date.date_input("End",max(engage['created_at']),min(engage['created_at']),max(engage['created_at']),key='end_date')

    likes, retweets, replies, quotes = st.columns(4)

    start = dt.fromordinal(start.toordinal()).astimezone(pytz.utc)
    end = dt.fromordinal(end.toordinal()).astimezone(pytz.utc)

    hashes = mutate_hastag_df(hashtags, start, end)
    df = mutate_engagement_df(engage, start, end)

    likes_metric, retweet_metric, reply_metric, quote_metric = calc_engagement_metrics(df, baseline)

    likes.metric('Avg Likes',f'{likes_metric[0]}', f'{likes_metric[1]}')
    retweets.metric('Avg Retweets',f'{retweet_metric[0]}', f'{retweet_metric[1]}')
    replies.metric('Avg Replies',f'{reply_metric[0]}', f'{reply_metric[1]}')
    quotes.metric('Avg Quotes',f'{quote_metric[0]}', f'{quote_metric[1]}')

    col1, col2 = st.columns(2)
    
    fig = engagement_word_cloud(hashes)
    to_plot = engagement_time_series(df)


    col2.header('20 most popular hastags in this period')
    col2.pyplot(fig)

    col1.header('Likes and retweets of this period')
    col1.plotly_chart(to_plot)

with following:
    st.header("Geographical coverage of UNESCO's followers overlaid with field offices/institutions")
    st.pydeck_chart(following_graph(places, fos))

sentiment_order = ['very negative','negative','neutral','positive','very positive']
with sentiment:
    
    st.header('Sentiment of UNESCO in the last 2 weeks')
    sentiment_dist, word_cloud = st.columns(2) 

    to_plot = sentiment_distribution(mentions)

    # sentiment_dist.text('The')
    sentiment_dist.plotly_chart(to_plot)

    selection = word_cloud.radio('Sentiment category', sentiment_order, horizontal = True)
    convo_ids = mentions[mentions['sentiment']==selection]['conversation_id'].unique()
    fig = sentiment_word_cloud(convo_sentiment[convo_sentiment['conversation_id'].isin(convo_ids)])

    word_cloud.pyplot(fig)