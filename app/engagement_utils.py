import pandas as pd


def preprocess_engagement(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    
    df = pd.DataFrame(rows)
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['hashtags'].fillna('',inplace = True)
    df['bucket_idx'] = df['created_at'].dt.normalize()
    df['bucket'] = df['bucket_idx'].dt.strftime('%B, %Y')
    

    return df

def mutate_engagement_df(df, start, end):

    return df[(df['created_at'].between(start,end)) & (df['hashtags'].str.contains(r'[\w\d]+',regex = True))]

def calc_engagement_metrics(df, baseline):

    likes_view = round(df['like_count'].mean(), 1)
    retweet_view = round(df['retweet_count'].mean(), 1)
    reply_view = round(df['reply_count'].mean(), 1)
    quote_view = round(df['quote_count'].mean(), 1)


    likes_delta = round(likes_view - baseline["like_count"], 1)
    retweet_delta = round(retweet_view - baseline["retweet_count"], 1)
    reply_delta = round(reply_view - baseline["reply_count"],1)
    quote_delta = round(quote_view - baseline["quote_count"])

    return (likes_view, likes_delta), (retweet_view, retweet_delta), (reply_view, reply_delta), (quote_view, quote_delta)





    