import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from googletrans import Translator
import streamlit.components.v1 as components
from slider_utils import *
from filter_utils import *

st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

tabForFrequencySlider, tabForFrequencyFilter, tabForStatistics, tabForAbout = st.tabs(["Frequency Slider","Frequency Filter", "Statistics", "About"])

df = pd.read_csv('FP_KOS_2022.csv')

with tabForFrequencySlider:
    st.header("Frequency allocation based on slider")
    st.write(getSliderBounds())
    start_clr, end_clr = st.slider("Select a range of Frequencies",value=(0, 110), step=10, label_visibility="hidden")
    lowerBound = getLowerBoundAndFrequency(start_clr)[0]
    lowerFrequency = getLowerBoundAndFrequency(start_clr)[1]
    upperBound = getUpperBoundAndFrequency(end_clr)[0]
    upperFrequency = getUpperBoundAndFrequency(end_clr)[1]
    tabForLowerBounds, tabForUpperBounds, tabForBothBounds = st.tabs(["Lower Bound Frequencies", "Upper Bound Frequencies", "Lower and Upper Frequencies"])

    with tabForLowerBounds:
        selectedRows = df[(df["_lowerFrequency"] >= lowerBound) & (df["_lowerFrequency"] <= upperBound)]
        if(lowerFrequency != upperFrequency):
            st.subheader("You have selected the lower frequency records from " + lowerFrequency + " to " + upperFrequency)
        else:
            st.subheader("You have selected the lower frequency records in " + lowerFrequency)
        fig = px.scatter(
                selectedRows,
                x="_lowerFrequency",
                y="_term",
                size="_lowerFrequency",
                color="_term",
                hover_name="_term",
                log_x=True,
                size_max=60,)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        st.bar_chart(data=selectedRows, x='_term', y='_lowerFrequency', width=0, height=0, use_container_width=True)

    with tabForUpperBounds:
        selectedRows = df[(df["_higherFrequency"] >= lowerBound) & (df["_higherFrequency"] <= upperBound)]
        if(lowerFrequency != upperFrequency):
            st.subheader("You have selected the upper frequency records from " + lowerFrequency + " to " + upperFrequency)
        else:
            st.subheader("You have selected the upper frequency records in " + lowerFrequency)
        fig = px.scatter(
                selectedRows,
                x="_higherFrequency",
                y="_term",
                size="_higherFrequency",
                color="_term",
                hover_name="_term",
                log_x=True,
                size_max=60,)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        st.bar_chart(data=selectedRows, x='_term', y='_higherFrequency', width=0, height=0, use_container_width=True)

    with tabForBothBounds:
        selectedRows = df[(df["_lowerFrequency"] >= lowerBound) & (df["_higherFrequency"] <= upperBound)]
        if(lowerFrequency != upperFrequency):
            st.subheader("You have selected the records from " + lowerFrequency + " to " + upperFrequency)
        else:
            st.subheader("You have selected the frequency records in " + lowerFrequency)
        
        fig = px.scatter(
            selectedRows,
            x="_lowerFrequency",
            y="_higherFrequency",
            color="_term",
            hover_name="_term",
            log_x=True,
            size_max=1400,
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tabForFrequencyFilter:
    st.header("Frequency allocation based on filter")
    term = np.append("All", df['_term'].unique())
    
    with st.form(key='frequencyFilter'):
        col1,col2,col3, col4 = st.columns(4)
        with col1:
            frequencyBands = st.selectbox('Frequency bands',(getFrequencyBounds()))
        with col2:
            selectedTerm = st.selectbox('Term', options=list(term))
        with col3:
            selectedLanguage = st.selectbox('Language', (getLanguages()))
        with col4:
            searchType = st.radio("Status", ("primary", "secondary"))
            graphOrientation = st.radio("Graph orientation", ("Horizontal", "Vertical"))
            
        submit = st.form_submit_button(label='Search')

    if submit:
        lowerBound = getLowerBoundAndUpperBound(frequencyBands)[0]
        upperBound = getLowerBoundAndUpperBound(frequencyBands)[1]

        if(selectedTerm == "All"):
            dataset = df[
                (df['_lowerFrequency'] >= lowerBound) & 
                (df['_higherFrequency'] <= upperBound) & 
                (df['_status'] == searchType)]
        else:
            dataset = df[
                (df['_lowerFrequency'] >= lowerBound) & 
                (df['_higherFrequency'] <= upperBound) & 
                (df['_term'] == selectedTerm) & 
                (df['_status'] == searchType)]

        if(len(dataset) == 0):
            st.write("No data!")
        else:
            colors = getColors()

            graphContainer = []
            if(graphOrientation == "Horizontal"):
                with open("./css/horizontalStyles.css") as style:
                    graphContainer = [f""" </div><style>{style.read()}</style>"""]
            else:
                with open("./css/verticalStyles.css") as style:
                    graphContainer = [f""" </div> <style>{style.read()}</style>"""]

            graphContainer.append("<div class='containerSlider'>")
            datasetWithResetedIndexes = dataset.reset_index(drop=True)
            translator = Translator()
            languageAbbreviation = getAbbreviationForLanguage(selectedLanguage)

            for i in range(len(datasetWithResetedIndexes)):
                graphContainer.append(f"""
                <div style="background-color:{colors[i]};filter: invert(5);mix-blend-mode: difference;">
                    <h3>{translator.translate(datasetWithResetedIndexes["_term"].loc[i], dest=languageAbbreviation).text}</h3>
                    <p><b>{datasetWithResetedIndexes["_lowerFrequency"].loc[i]} Hz - {datasetWithResetedIndexes["_higherFrequency"].loc[i]} Hz</b></p>
                </div>""")
            
            components.html("".join(graphContainer), height=200, scrolling=True)
    
with tabForStatistics:
   st.header("Statistics for experts")
   with st.form(key='statistics'):
        st.subheader("Search if a specific frequency is free!")
        col1,col2,col3 = st.columns(3)
        
        with col1:
           number = st.number_input('Insert a number')  
        with col2:
            frequencyUnit = st.selectbox('Frequency Units',(
                'KHz',
                'MHz',
                'GHz',))
        with col3:
            frequency = st.selectbox('Higher/lower',(
                'Lower Frequency',
                'Higher Frequency',))
        
        submit_search = st.form_submit_button(label='Search')

        freeFrequency=[]
        if submit_search:
            if frequency=='Lower Frequency':
                if frequencyUnit =='KHz':
                    freeFrequency = df[(df["_lowerFrequency"] == number*1000)]
                elif frequencyUnit=='MHz':
                    freeFrequency = df[(df["_lowerFrequency"] == number*1000000)]
                elif frequencyUnit=='GHz':
                    freeFrequency = df[(df["_lowerFrequency"] == number*1000000000)]
            else:
                if frequencyUnit =='KHz':
                    freeFrequency = df[(df["_higherFrequency"] == number*1000)]
                elif frequencyUnit=='MHz':
                    freeFrequency = df[(df["_higherFrequency"] == number*1000000)]
                elif frequencyUnit=='GHz':
                    freeFrequency = df[(df["_higherFrequency"] == number*1000000000)]

            if len(freeFrequency)>0:
                st.write("There are ", len(freeFrequency), " rows in this frequency")
                st.write(freeFrequency.drop(['_shortComments'],axis=1))
            else:
                st.write("This frequency is **:green[free]**")
        
   with st.form(key='statistics_groupByTerm'):
        st.subheader("Group by Frequency Term")
        term=df['_term'].unique()
        frequencyTerm = st.selectbox('Frequency Term',(term))
        submit_search = st.form_submit_button(label='Search')

        if submit_search:
            GroupByTerm = df[(df["_term"] == frequencyTerm)]
            tabTable, tabPlot= st.tabs(["table", "plot"])

            with tabTable:
                st.write(GroupByTerm.drop(['_shortComments'],axis=1))
            with tabPlot:
                fig = px.scatter(
                    GroupByTerm,
                    x="_lowerFrequency",
                    y="_status",
                    size="_lowerFrequency",
                    color="_lowerFrequency",
                    hover_name="_status",
                    log_x=True,
                    size_max=60,)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)

   with st.form(key='statistics_groupByStatus'):
        st.subheader("Group by Frequency Status")        
        status=df['_status'].unique()
        frequencyStatus = st.selectbox('Frequency Status',(status))
        submit_search = st.form_submit_button(label='Search')

        if submit_search:
            GroupByStatus = df[(df["_status"] == frequencyStatus)]
            tabTable, tabPlot= st.tabs(["table", "plot"])

            with tabTable:
                st.write(GroupByStatus.drop(['_shortComments'],axis=1))
            with tabPlot:
                fig = px.scatter(
                    GroupByStatus,
                    x="_lowerFrequency",
                    y="_term",
                    size="_lowerFrequency",
                    color="_term",
                    hover_name="_higherFrequency",
                    log_x=True,
                    size_max=60,)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                
with tabForAbout:
   st.header("About")
   st.subheader("P??rshkrimi i projektit")
   st.markdown('Ky projekt ??sht?? zhvilluar n?? kuad??r t?? Universitetit t?? Prishtin??s t?? nivelit master departmenti **Inxhinieri Kompjuterike** p??r digjitalizim t?? sherbimeve t?? ARKEP: Vizualizimi interaktiv ne Ueb i te dhenave te planit frekuencor. T?? dh??nat jan?? marr?? nga ARKEP dhe jan?? shfyt??zuar gjat?? zhvillimit dhe testimit t?? programit.')
   st.markdown("Ky projekt ??sht?? zhvilluar n?? gjuh??n programuese :red[Python] dhe jan?? p??rdorur librarit?? **:blue[Streamlit]**, **:blue[Pandas]**, **:blue[numpy]**,**:blue[ploty.express]**, **:blue[seaborn]**, **:blue[matplotlib]** p??r vizualizim dhe **:blue[googletrans] p??r p??rkthim**.")
   st.markdown("https://streamlit.io/")
   st.markdown("https://docs.python.org/3/")
   st.markdown("https://numpy.org/doc/")
   st.markdown("https://plotly.com/python/plotly-express/")
   st.markdown("https://seaborn.pydata.org/")
   st.markdown("https://matplotlib.org/stable/index.html")
   st.markdown("https://py-googletrans.readthedocs.io/en/latest/")
   st.subheader('P??rshkrimi i datasetit')
   st.markdown('Dataseti q?? kemi p??rdorur n?? k??t?? projket ??sht?? shp??rndarja dhe aplikimi i radio-frekuencave n?? Republik??n e Kosov??s q?? i takojn brezit nga 8.3KHz deri n?? 3000GHz, i cili na ??sht?? dh??n?? nga ARKEP. Ky dataset p??rmban frekuenc??n e ul??t, frekuenc??n e lart, statusin dhe llojin e frekunec??s, dhe p??rmban rreth 1431 t?? dh??na.')
   st.subheader("Ky projekt ??sht?? zhvilluar nga:")
   st.markdown("Elvir Misini -- elvir.misini@student.uni-pr.edu")
   st.markdown("Uran Laj??i -- uran.lajci@student.uni-pr.edu")