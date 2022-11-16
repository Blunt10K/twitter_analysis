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

    hashtags = preprocess_hashtags(_conn, st.secrets['tweets_url'])

    places = preprocess_places(_conn, st.secrets['places_url'])

    places = preprocess_following(_conn, st.secrets['following_url'], places)

    fos = preprocess_fo(_conn, st.secrets['fo_url'])

    mentions, convo_sentiment = preprocess_sentiment(_conn, st.secrets['ment_url'],st.secrets['roots_url'])

    return engagement, hashtags, baseline, places, fos, mentions, convo_sentiment

conn = connect_sheets()

engage, hashtags, baseline, places, fos, mentions, convo_sentiment = load_data(conn)
following, engagement,  sentiment, events = st.tabs(['Following','Engagement','Sentiment','Noteable events'])

if 'sentiment_mkd' not in st.session_state:
    st.session_state['sentiment_mkd'] = 'very negative' 

with following:
    st.header("Geographical coverage of UNESCO's followers overlaid with field offices/institutions")
    st.pydeck_chart(following_graph(places, fos))

with engagement:
    st.subheader('Select a period')
    start_date, end_date = st.columns(2)

    start = start_date.date_input("Start",min(engage['created_at']),min(engage['created_at']),
            max(engage['created_at']),key='start_date')
    end = end_date.date_input("End",max(engage['created_at']),min(engage['created_at']),max(engage['created_at']),key='end_date')
    st.subheader('Engagement with UNESCO for this period')
    likes, retweets, replies, quotes = st.columns(4)

    start = dt.fromordinal(start.toordinal()).astimezone(pytz.utc)
    end = dt.fromordinal(end.toordinal()).astimezone(pytz.utc)

    hashes = mutate_hastag_df(hashtags, start, end)
    df = mutate_engagement_df(engage, start, end)

    likes_metric, retweet_metric, reply_metric, quote_metric = calc_engagement_metrics(df, baseline)

    likes.metric('Avg Likes',f'{likes_metric[0]}')
    retweets.metric('Avg Retweets',f'{retweet_metric[0]}')
    replies.metric('Avg Replies',f'{reply_metric[0]}')
    quotes.metric('Avg Quotes',f'{quote_metric[0]}')

    col1, col2 = st.columns(2)
    
    fig = engagement_word_cloud(hashes)
    to_plot = engagement_time_series(df)


    col2.subheader('20 most popular hastags in this period')
    col2.pyplot(fig)

    col1.subheader('Likes and retweets of this period')
    col1.plotly_chart(to_plot)

sentiment_order = ['very negative','negative','neutral','positive','very positive']
with sentiment:
        
    sentiment_dist, word_cloud = st.columns(2) 
    sentiment_dist.markdown('### Sentiment of Tweets mentioning UNESCO in the last 2 weeks')
    to_plot = sentiment_distribution(mentions)

    # sentiment_dist.text('The')
    sentiment_dist.plotly_chart(to_plot)
    
    selection = word_cloud.radio('Sentiment category', sentiment_order, horizontal = True,
            label_visibility='hidden')
    word_cloud.markdown(f'### Popular words that elicit {selection} sentiment')
    convo_ids = mentions[mentions['sentiment']==selection]['conversation_id'].unique()
    fig = sentiment_word_cloud(convo_sentiment[convo_sentiment['conversation_id'].isin(convo_ids)])

    word_cloud.pyplot(fig)

with events:
    pic1, pic2 = st.columns(2)
    pic2.image('https://raw.githubusercontent.com/Blunt10K/twitter_analysis/main/app/images/call_to_action.png', caption = 'Mobilisation of UNESCO staff')
    pic1.image('https://raw.githubusercontent.com/Blunt10K/twitter_analysis/main/app/images/malaysia.png', caption = 'Flooding in Malaysia')