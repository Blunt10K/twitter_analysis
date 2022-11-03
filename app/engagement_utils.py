import pandas as pd


def preprocess_engagement(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    
    df = pd.DataFrame(rows)
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['hashtags'].fillna('',inplace = True)
    df['bucket'] = df['created_at'].dt.strftime('%B, %Y')
    df['bucket_idx'] = pd.to_datetime(df['bucket'],format = '%B, %Y',utc = True)

    return df

def mutate_engagement_df(analysis, start, end):

    df = analysis[analysis['created_at'].between(start,end)]
    return df[df['hashtags'].str.contains(r'[\w\d]+',regex = True)]

def calc_engagement_metrics(df, baseline):

    likes_view = df['like_count'].mean()
    retweet_view = df['retweet_count'].mean()
    reply_view = df['reply_count'].mean()
    quote_view = df['quote_count'].mean()


    likes_delta = round(likes_view - baseline["like_count"], 1)
    retweet_delta = round(retweet_view - baseline["retweet_count"], 1)
    reply_delta = round(reply_view - baseline["reply_count"],1)
    quote_delta = round(quote_view - baseline["quote_count"])

    return (likes_view, likes_delta), (retweet_view, retweet_delta), (reply_view, reply_delta), (quote_view, quote_delta)





    