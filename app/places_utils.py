import pandas as pd

def preprocess_places(rows):

    df = pd.DataFrame(rows)
    df = df.dropna()

    return df