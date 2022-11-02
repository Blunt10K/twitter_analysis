import pandas as pd

def preprocess_following(conn, sheet_url, places):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()

    df = pd.DataFrame(rows)
    df = df.join(places.set_index('place'), on = 'location', how = 'inner')

    df = df.groupby(['longitude','latitude'], as_index = False).sum(numeric_only=True)

    df['radii'] = 50*(df['followers_count']/df['followers_count'].max())


    return df