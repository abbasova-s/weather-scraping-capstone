import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px


# Page layout
st.set_page_config(
    page_title="Weather Around The World",
    layout="wide")

# Load the weather data from SQLite
conn = sqlite3.connect("weather.db")
df = pd.read_sql_query("SELECT * FROM weather_clean", conn)
conn.close()


st.title("Weather Around The World")
st.subheader("This dashboard explores weather conditions and temperatures in different cities around the world.")

# Create two side-by-side columns
col1, col2 = st.columns(2)

with col1:
    # Visualization 1 - Temperature by city
    st.header("Temperature by City")
    st.write("This chart shows the temperatures of one or more selected cities.")

    selected_cities = st.multiselect("Select cities to compare their temperatures:", options=df['City'].unique(), default=df['City'].unique())

    filtered_df = df[df["City"].isin(selected_cities)]

    bar_chart = px.bar (filtered_df, x='City', y='Temperature')

    st.plotly_chart(bar_chart)

with col2:
    # Visualization 2 - Temperature distribution
    st.header("Temperature Distribution")
    st.write("This chart shows the overall distribution of temperatures.")

    min_temp = int(df["Temperature"].min())
    max_temp = int(df["Temperature"].max())

    selected_temp = st.slider("Select a temperature range: (°F)", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))

    filtered_temp_df = df[df["Temperature"].between(selected_temp[0], selected_temp[1])]

    histogram = px.histogram(filtered_temp_df, x='Temperature', nbins=10)
    st.plotly_chart(histogram)


# Visualization 3 - Weather conditions
st.header("Number of Cities by Weather Condition")
st.write("This chart shows how many cities have each weather condition.")

st.sidebar.title("Dashboard Filters")
selected_conditions = st.sidebar.multiselect("Select weather conditions:", options=df["Weather description"].unique(), default=df["Weather description"].unique())


filtered_cond_df = df[df["Weather description"].isin(selected_conditions)]

conditions_df = (filtered_cond_df["Weather description"].value_counts().reset_index())
conditions_df.columns = ["Weather description", "Number of Cities"]
conditions_chart = px.bar (conditions_df, x='Weather description', y='Number of Cities', barmode='group')

st.plotly_chart(conditions_chart)
