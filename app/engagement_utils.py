import pandas as pd


def preprocess_engagement(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    
    df = pd.DataFrame(rows)
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at'] =  df['created_at'].dt.normalize()
    df.sort_values('created_at', inplace=True)

    df.rename(columns={'retweet_count':'retweets','like_count':'likes',
                       'reply_count':'replies','quote_count':'quotes'}, inplace= True)

    

    return df


def preprocess_hashtags(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    
    df = pd.DataFrame(rows)
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['hashtags'].fillna('',inplace = True)
    df['bucket_idx'] = df['created_at'].dt.normalize()
    df['bucket'] = df['bucket_idx'].dt.strftime('%B, %Y')
    

    return df

def mutate_hastag_df(df, start, end):

    return df[(df['created_at'].between(start,end)) & (df['hashtags'].str.contains(r'[\w\d]+',regex = True))]


def mutate_engagement_df(df, start, end):

    return df[(df['created_at'].between(start,end))]

def calc_engagement_metrics(df, baseline):

    likes_view = round(df['likes'].mean(), 1)
    retweet_view = round(df['retweets'].mean(), 1)
    reply_view = round(df['replies'].mean(), 1)
    quote_view = round(df['quotes'].mean(), 1)


    likes_delta = round(likes_view - baseline["likes"],1)
    retweet_delta = round(retweet_view - baseline["retweets"],1)
    reply_delta = round(reply_view - baseline["replies"],1)
    quote_delta = round(quote_view - baseline["quotes"],1)

    return (likes_view, likes_delta), (retweet_view, retweet_delta), (reply_view, reply_delta), (quote_view, quote_delta)

    