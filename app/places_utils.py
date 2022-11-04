import pandas as pd

def preprocess_places(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    

    df = pd.DataFrame(rows)
    df = df.dropna()

    return df

def preprocess_fo(conn, sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()

    df = pd.DataFrame(rows)
    
    df.columns = [i.lower() for i in df.columns]
    df['radii'] = 500000

    return df