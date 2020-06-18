#!/usr/bin/python
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import folium
from folium.plugins import HeatMap
import time
import os
#import plotly.graph_objs as go

@st.cache
def load_image(img):
	im =Image.open(os.path.join(img))
	return im

# To Improve speed and cache data
@st.cache(persist=True)
def explore_data(dataset):
	df = pd.read_csv(os.path.join(dataset))
	return df 
    

@st.cache
def loadData():
    df = explore_data('datasets_700807_1225257_Worldwide-Earthquake-database.csv')
    total = df.isnull().sum().sort_values(ascending=False)
    percent = (df.isnull().sum()
               / df.isnull().count()).sort_values(ascending=False)
    missing_data = pd.concat([total, percent], axis=1, keys=['Total',
                             'Percent'])
    cols = missing_data.head(10).index
    df = df.drop(cols, axis='columns')
    return df


def main():
    st.title('EARTHQUAKE DATA VISUALIZATION WEB APP!')
    st.subheader('Data Visualization')
    data = loadData()

    our_image = load_image('Palu_ARIA_DPM_large_smooth_v0.7_figure.jpg')
    with st.spinner("Waiting.."):
        time.sleep(5)
    st.success("Finished Loading!!")   
    st.image(our_image)
    # Insert Check-Box to show the snippet of the data.
    '''
## Earthquake explorer
An earthquake (also known as a quake, tremor or temblor) is the shaking of the surface of the Earth resulting from a sudden release of energy in the Earth's lithosphere that creates seismic waves. 
Earthquakes can range in size from those that are so weak that they cannot be felt to those violent enough to propel objects and people into the air, and wreak destruction across entire cities. 
\n\nThe seismicity, or seismic activity, of an area is the frequency, type, and size of earthquakes experienced over a period of time.
The word tremor is also used for non-earthquake seismic rumbling.
At the Earth's surface, earthquakes manifest themselves by shaking and displacing or disrupting the ground. When the epicenter of a large earthquake is located offshore, the seabed may be displaced sufficiently to cause a tsunami. Earthquakes can also trigger landslides and occasionally, volcanic activity.
    '''

    if st.checkbox('Show Earthquake Data'):
        st.subheader('Showing Earthquake Data')

        st.dataframe(data.head(100))

    # ML Section

    choose_viz = st.sidebar.selectbox('Choose The Visualization', [ 'COUNT OF EARTHQAKE PER YEAR','EARTHQAKE RESULTING IN TSUNAMI', 'MOST NO OF EARTHQAKE','MOST NO OF TSUNAMI','MEAN EARTHQAKE INTENSITY','MOST NO OF DEATHS DUE TO  EARTHQAKE','LOCATION WITH MOST NO OF EARTHQAKE','MOST INTANSE EARTHQUAKES (MAGNITUDE>8)'])
    
    # ABOUT
    if choose_viz == 'COUNT OF EARTHQAKE PER YEAR':
        #data =  data[data >0]

        year = st.sidebar.slider('Select year', min_value=1900, max_value=2020, value=1940)
        data= data[(data['YEAR']<=year) & (data['YEAR']>=1900)]
        #st.write(data)
        X = data.groupby('YEAR')['COUNTRY'].count()
        #st.write(X)
        fig = px.line(X, labels={'x': 'years', 'y': 'Count'}, height=600)
        st.plotly_chart(fig)

    elif choose_viz == 'EARTHQAKE RESULTING IN TSUNAMI':

        labels = ['No = No Tsunami','Yes = Tsunami']
        X = data['FLAG_TSUNAMI'].value_counts(sort=True)
        #st.write(X)
        fig = px.pie(X,values='FLAG_TSUNAMI',names=labels, title='% of Earthquakes resulting in Tsunami')
        st.plotly_chart(fig)
        st.write("Due to earthquake almost 30% Tsunami occured")

    elif choose_viz =='MOST NO OF EARTHQAKE':
        country =  data.groupby("COUNTRY")["YEAR"]
        x=country.count().sort_values(ascending=False).head(20)
        fig=px.bar(x, orientation='h', height=600,title='Most number of Earthquakes')
        st.plotly_chart(fig)
        st.write("Above data is only for top 20 country. I have first filter the data from 1900 to 2020 as the original data was containing negative values which was misspelled. The China has faced highest number of earth quake more than 550 times from 1900 to 2020.Indonesia is legging China by  almost 200 counts")
    elif choose_viz == 'MOST INTANSE EARTHQUAKES (MAGNITUDE>8)':
        df_select_8 = data[data.EQ_MAG_MW > 8]
        df_select_8.LATITUDE =  pd.to_numeric(df_select_8.LATITUDE)
        df_select_8.LONGITUDE =  pd.to_numeric(df_select_8.LONGITUDE)
        #st.write(df_select_8.LONGITUDE)
        sel_columns = ['I_D','YEAR','EQ_MAG_MW','LATITUDE','LONGITUDE']
        df_select_8=  df_select_8[sel_columns]
        zoom_factor = 1.1
        # use heatmap to display many earthquakes
        m= folium.Map(location=[0,0],zoom_start=zoom_factor)
        HeatMap(data=df_select_8[['LATITUDE', 'LONGITUDE']], radius=10).add_to(m)
        #m.save('C:/Users/mohdf/OneDrive/Desktop/streamlit/Earthquake_web_app/EarthQuake-Explorer-Web-App/map.html')
        #map_path= 'C:/Users/mohdf/AppData/Roaming/Python/Python37/site-packages/streamlit/static/'+'map.html'
        our_image = load_image('map1.jpg')
        st.image(our_image)
        
        #st.markdown('<iframe src="C:/Users/mohdf/OneDrive/Desktop/streamlit/EarthQuake/map.html"> </iframe>')
        #st.write(m._repr_html_(), unsafe_allow_html=True)

    elif choose_viz =='MOST NO OF TSUNAMI':
        country_T =  data[data["FLAG_TSUNAMI"] =='Yes'].groupby("COUNTRY")["YEAR"]
        country_T=   country_T.count().sort_values(ascending=False).head(20)
        fig  =  px.bar(country_T, orientation='h', height=600, title="Most number of Tsunami")
        st.plotly_chart(fig)
        st.write("Japan has faced highest number of Tsunami from 1900 to 2020.")

    elif choose_viz =='MEAN EARTHQAKE INTENSITY':
        x = data.groupby("COUNTRY")["INTENSITY"].mean().sort_values()
        fig  =  px.choropleth(x,locations =x.index,   locationmode = 'country names',height=700 ,color =x,hover_name ="INTENSITY",color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(title_text= 'Mean Earthquake Intensity' , height=500)
        st.plotly_chart(fig)

    elif choose_viz =='MOST NO OF DEATHS DUE TO  EARTHQAKE':
        country =  data.groupby("COUNTRY")["TOTAL_DEATHS"].sum()
        x=country.sort_values(ascending=False).head(20)
        fig=px.bar(x, orientation='h', height=600,title='Most number of Deaths due to  Earthquakes')
        st.plotly_chart(fig)    
        
    elif choose_viz =='LOCATION WITH MOST NO OF EARTHQAKE':
        country =  data.groupby("LOCATION_NAME")["EQ_PRIMARY"].count().sort_values(ascending=False).head(20)
        fig=px.bar(country, orientation='h', height=600,title='Location with Most number of Earthquakes')
        st.plotly_chart(fig)
        st.write("By seeing the plot we can say that  Yunnan Province is the epi center of Earthquake in China")

    st.sidebar.header('About')
    st.sidebar.info('Data is been collected from  the Kaggle  website.\n\n'+'A Web App Developed by MOHD FAHAD.\n\n' + \
        '(c) 2020.')
    st.sidebar.markdown('---')         







if __name__ == '__main__':
    main()


            
