import streamlit as st
import plotly.io as pio
from datetime import datetime as dt
from datetime import timedelta as td
from engagement_utils import *
from graphs import *
from google.oauth2 import service_account
from gsheetsdb import connect
from places_utils import *
from following_utils import *
import pytz

st.set_page_config(page_title='UNESCO Twitter presence',layout='wide')

pio.templates.default = 'plotly_white'

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


st.experimental_memo(persist='disk')
def get_data():
    conn = connect_sheets()

    sheet_url = st.secrets["tweets_url"]
    engagement = preprocess_engagement(conn, sheet_url)
    baseline = engagement.mean(numeric_only=True)

    sheet_url = st.secrets["places_url"]
    places = preprocess_places(conn, sheet_url)

    sheet_url = st.secrets["following_url"]
    places = preprocess_following(conn, sheet_url, places)

    sheet_url = st.secrets["fo_url"]
    fos = preprocess_fo(conn, sheet_url)

    return engagement, baseline, places, fos

analysis, baseline, places, fos = get_data()

engagement, following, sentiment = st.tabs(['Engagement', 'Following','Sentiment'])

# with st.sidebar:
#     st.header("Engagement over the following period")
#     start = st.date_input("Start",min(analysis['created_at']),min(analysis['created_at']),max(analysis['created_at']))
#     end = st.date_input("End",max(analysis['created_at']),start + td(days=1),max(analysis['created_at']))
    

with engagement:
    st.header('Engagement with UNESCO from:')
    start_date, end_date = st.columns(2)

    start = start_date.date_input("Start",min(analysis['created_at']),min(analysis['created_at']),max(analysis['created_at']))
    end = end_date.date_input("End",max(analysis['created_at']),start + td(days=1),max(analysis['created_at']))

    likes, retweets, replies, quotes = st.columns(4)

    start = dt.fromordinal(start.toordinal()).astimezone(pytz.utc)
    end = dt.fromordinal(end.toordinal()).astimezone(pytz.utc)

    df = mutate_engagement_df(analysis, start, end)

    likes_metric, retweet_metric, reply_metric, quote_metric = calc_engagement_metrics(df, baseline)

    likes.metric('Avg Likes',f'{round(likes_metric[0],1)}', f'{likes_metric[1]}')
    retweets.metric('Avg Retweets',f'{round(retweet_metric[0],1)}', f'{retweet_metric[1]}')
    replies.metric('Avg Replies',f'{round(reply_metric[0],1)}', f'{reply_metric[1]}')
    quotes.metric('Avg Quotes',f'{round(quote_metric[0],1)}', f'{quote_metric[1]}')

    col1, col2 = st.columns(2)
    
    fig = engagement_word_cloud(df[df['bucket_idx'].between(start,end)])
    to_plot = engagement_time_series(df[df['bucket_idx'].between(start,end)])


    col2.header('20 most popular hastags in this period')
    col2.pyplot(fig)

    col1.header('Metrics of hashtags per month')
    col1.plotly_chart(to_plot)

with following:
    st.header('Geographical coverage of UNESCO\'s followers overlaid with field offices/institutions')
    st.pydeck_chart(following_graph(places, fos))