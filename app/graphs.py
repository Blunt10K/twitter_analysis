from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
import matplotlib.pyplot as plt
import pydeck as pdk
import re

template = 'plotly_white'
stop_words = STOPWORDS
stop_words.add('say')
stop_words.add('day')
stop_words.add('now')
stop_words.add('amp')


def engagement_word_cloud(df):
    wc_data = df.groupby('hashtags').sum(numeric_only=True)
    wc = wc_data.to_dict()['like_count']

    cloud = WordCloud(min_word_length=3, colormap = 'winter',max_words=20,width = 400, height = 200,prefer_horizontal = 0.95,
            background_color = 'white',collocations = False, stopwords=STOPWORDS).generate_from_frequencies(wc)
    
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(cloud)

    return fig

def sentiment_word_cloud(df):
    text = ' '.join(df['text'])
    text = re.sub(r'[^a-zA-Z0-9\s]','', text)

    cloud = WordCloud(min_word_length=3, colormap = 'winter',max_words=100,#width = 400, height = 200,
    prefer_horizontal = 0.95,
            background_color = 'white',collocations = False, stopwords=stop_words).generate(text)

    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(cloud)

    return fig

def engagement_time_series(df):
    to_plot = df.groupby('created_at',as_index=False).sum()
    to_plot = to_plot.rolling(7,on = 'created_at',min_periods = 1).mean()

    to_plot = px.line(to_plot, x = 'created_at',y = ['likes','retweets'],template = template,
        labels={"variable": "metric",'created_at':'date of tweet','value':'count'},
        width = 800, height = 500
    )
    # rf = df.groupby(['bucket','bucket_idx','hashtags'],as_index=False).sum(numeric_only=True).sort_values('bucket_idx')
    # to_plot = px.scatter(rf,x='like_count', y='retweet_count',size = 'reply_count', size_max = 55,color = 'quote_count',
    #     animation_group='hashtags',animation_frame='bucket',width = 800, height = 500,hover_name='hashtags',
    #     color_continuous_scale = px.colors.sequential.Agsunset, range_x=[-1000,rf['like_count'].max()+1000],
    #     range_y=[-1000,rf['retweet_count'].max()+1000])

    # to_plot.update_xaxes(zeroline = True)
    # to_plot.update_yaxes(zeroline = True)

    return to_plot

def following_graph(df, fos):
    
    field_offices = pdk.Layer(
            'ScatterplotLayer',
            data=fos,
            get_position=['longitude', 'latitude'],
            get_color=[200, 30, 0, 50],
            radius_scale=5,
            radius_min_pixels=1,
            radius_max_pixels=10,
            get_radius='radii')

    followers = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            radius_scale=5,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=['longitude', 'latitude'],
            get_color=[0, 119, 212, 160],
            get_radius="radii")


    return pdk.Deck(layers=[followers, field_offices], map_style = 'light')

def sentiment_distribution(df):
    cat_orders = {'sentiment':['very negative','negative','neutral','positive','very positive']}
    colors = px.colors.qualitative.Plotly
    neutral = px.colors.qualitative.Set1[8]
    colour_map = {'very negative':colors[1],'negative':colors[4],'neutral':neutral,
                  'positive':colors[5],'very positive':colors[0]}

    title = "Sentiment distribution of UNESCO's mentions"

    return (px.histogram(df,x='sentiment',color='sentiment',category_orders=cat_orders,
    color_discrete_map=colour_map,template=template,width = 800, height = 500)
            .update_layout(showlegend = False))