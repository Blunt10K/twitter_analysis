import pandas as pd

def preprocess_following(rows, places):

    df = pd.DataFrame(rows)
    df = df.join(places.set_index('place'), on = 'location', how = 'inner')

    df = df.groupby(['longitude','latitude'], as_index = False).sum(numeric_only=True)


    return df