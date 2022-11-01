from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt


def engagement_word_cloud(df):
    wc_data = df.groupby('hashtags').sum(numeric_only=True)
    wc = wc_data.to_dict()['like_count']

    cloud = WordCloud(min_word_length=3, colormap = 'winter',max_words=20,width = 400, height = 200,prefer_horizontal = 0.95,
            background_color = 'white',collocations = False).generate_from_frequencies(wc)
    
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(cloud)

    return fig

def engagement_time_series(df):
    rf = df.groupby(['bucket','bucket_idx','hashtags'],as_index=False).sum(numeric_only=True).sort_values('bucket_idx')
    to_plot = px.scatter(rf,x='like_count', y='retweet_count',size = 'reply_count', size_max = 55,color = 'quote_count',
        animation_group='hashtags',animation_frame='bucket',width = 800, height = 500,hover_name='hashtags',
        color_continuous_scale = px.colors.sequential.Agsunset, range_x=[-1000,rf['like_count'].max()+1000],
        range_y=[-1000,rf['retweet_count'].max()+1000])

    to_plot.update_xaxes(zeroline = True)
    to_plot.update_yaxes(zeroline = True)

    return to_plot