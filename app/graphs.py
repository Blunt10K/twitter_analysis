from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt
import pydeck as pdk

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

def following_graph(df):
    layer = pdk.Layer(
        'HexagonLayer',
        df,
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        elevation_range=[0, 10000],
        extruded=True,
        coverage=1)

    scatter = pdk.Layer(
        'ScatterplotLayer',
            data=df,
            radius_scale=1,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=['longitude', 'latitude'],
            get_color='[200, 30, 0, 160]',
            get_radius="followers_count"
    )
    return pdk.Deck(layers=[layer,scatter])