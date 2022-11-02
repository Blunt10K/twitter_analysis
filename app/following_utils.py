import pandas as pd

def preprocess_following(rows, places):

    df = pd.DataFrame(rows)
    df = pd.concat((df, pd.json_normalize(df['public_metrics'])), axis = 1)
    df = df.join(places.set_index('place'), on = 'location', how = 'inner')

    df = df.groupby(['longitude','latitude'], as_index = False).sum(numeric_only=True)


    return df