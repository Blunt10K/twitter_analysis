import streamlit as st
import plotly.io as pio
from datetime import datetime as dt
from datetime import timedelta as td
from engagement_utils import *
from graphs import *
from google.oauth2 import service_account
from gsheetsdb import connect


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

# @st.experimental_memo(ttl=600)
# def run_query(query):
    
#     names = list(df['Resource'].unique())
#     names.sort()

#     return names, df

st.cache(persist=True)
def get_data():
    sheet_url = st.secrets["tweets_url"]
    conn = connect_sheets()

    query = f'SELECT * FROM "{sheet_url}"'

    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    
    df = preprocess_engagement(rows)
    baseline = df.mean(numeric_only=True)

    return df, baseline

analysis, baseline = get_data()

st.header('Engagement with UNESCO posts')

engagement, following, sentiment = st.tabs(['Engagement', 'Following','Sentiment'])

with engagement:
    with st.sidebar:
        st.header("Engagement over the following period")
        start = st.date_input("Start",min(analysis['created_at']),min(analysis['created_at']),max(analysis['created_at']))
        end = st.date_input("End",max(analysis['created_at']),start + td(days=1),max(analysis['created_at']))

    likes, retweets, replies, quotes = st.columns(4)

    start = dt.fromordinal(start.toordinal()).astimezone()
    end = dt.fromordinal(end.toordinal()).astimezone()

    df = mutate_engagement_df(analysis, start, end)

    likes_metric, retweet_metric, reply_metric, quote_metric = calc_engagement_metrics(df, baseline)

    likes.metric('Avg Likes',f'{round(likes_metric[0],1)}', f'{likes_metric[1]}')
    retweets.metric('Avg Retweets',f'{round(retweet_metric[0],1)}', f'{retweet_metric[1]}')
    replies.metric('Avg Replies',f'{round(reply_metric[0],1)}', f'{reply_metric[1]}')
    quotes.metric('Avg Quotes',f'{round(quote_metric[0],1)}', f'{quote_metric[1]}')

    

    col1, col2 = st.columns(2)
    

    fig = engagement_word_cloud(df)
    to_plot = engagement_time_series(df)


    col2.header('20 most popular hastags')
    col2.pyplot(fig)

    col1.header('Time series of hashtags per month')
    col1.plotly_chart(to_plot)