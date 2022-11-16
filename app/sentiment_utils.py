import pandas as pd

def preprocess_sentiment(conn, mentions_url, roots_url):
    query = f'SELECT * FROM "{mentions_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()

    mentions = pd.DataFrame(rows)
    avg_sent = mentions.groupby('conversation_id').mean(numeric_only = True)

    query = f'SELECT * FROM "{roots_url}"'
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()

    roots = pd.DataFrame(rows)

    word_cloud = roots.join(avg_sent, on ='conversation_id', how= 'inner')

    word_cloud['sentiment'] = ''
    word_cloud['sentiment'].mask((word_cloud['p_pos'] > 0.55) & (word_cloud['p_pos'] <= 0.65),'neutral',inplace=True)
    word_cloud['sentiment'].mask((word_cloud['p_pos'] < 0.3),'very negative',inplace=True)
    word_cloud['sentiment'].mask((word_cloud['p_pos'] > 0.3) & (word_cloud['p_pos'] <= 0.55),'negative',inplace=True)
    word_cloud['sentiment'].mask((word_cloud['p_pos'] > 0.9),'very positive',inplace=True)
    word_cloud['sentiment'].mask((word_cloud['p_pos'] > 0.65) & (word_cloud['p_pos'] <= 0.9),'positive',inplace=True)

    word_cloud.rename(columns = {'p_pos':'avg_prob'}, inplace = True)

    return mentions, word_cloud