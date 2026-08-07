import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, URL, text
from dotenv import load_dotenv
import os
import altair as alt

load_dotenv()

url_object = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_DB_HOST"),
    database=os.getenv("POSTGRES_DB"))

engine = create_engine(url_object)

rating_query = """ SELECT 
    EXTRACT(YEAR FROM release_date) AS year,
    AVG(vote_average) AS avg_rating
FROM fact_movies
WHERE vote_average IS NOT NULL
GROUP BY EXTRACT(YEAR FROM release_date)
ORDER BY year """

budget_query = """ SELECT 
    EXTRACT(YEAR FROM release_date) AS year,
    AVG(budget) AS avg_budget
FROM fact_movies
WHERE budget IS NOT NULL
GROUP BY EXTRACT(YEAR FROM release_date)
ORDER BY year """

cast_query = """
    SELECT dc.cast_name, COUNT(*) AS num_movies
    FROM dim_cast dc
    JOIN bridge_cast bc ON dc.cast_id = bc.cast_id
    GROUP BY dc.cast_name
    ORDER BY num_movies DESC
    LIMIT 20
"""

genre_query = """
    SELECT 
        dg.genre_name, 
        AVG(fm.vote_average) AS avg_rating,
        EXTRACT(YEAR FROM fm.release_date) AS year
    FROM dim_genres dg
    JOIN bridge_genres bg ON dg.genre_id = bg.genre_id
    JOIN fact_movies fm ON bg.movie_id = fm.movie_id
    WHERE fm.vote_average IS NOT NULL
    GROUP BY dg.genre_name, EXTRACT(YEAR FROM fm.release_date)
    ORDER BY year, avg_rating DESC
"""

budget_rating_query = """
    SELECT budget, vote_average
    FROM fact_movies
    WHERE budget IS NOT NULL AND vote_average IS NOT NULL AND vote_average>0
"""

rating_df = pd.read_sql(rating_query, con=engine)
rating_df['year'] = rating_df['year'].astype(int).astype(str)

st.markdown("<h2 style='text-align: center;'>Average Rating By Year</h2>",
            unsafe_allow_html=True)

st.line_chart(rating_df.set_index('year'),
              x_label="Year", y_label="Average Rating")

budget_df = pd.read_sql(budget_query, con=engine)
budget_df['year'] = budget_df['year'].astype(int).astype(str)


st.markdown("<h2 style='text-align: center;'>Average Budget By Year</h2>",
            unsafe_allow_html=True)

st.line_chart(budget_df.set_index('year'),
              x_label="Year", y_label="Average Budget")


cast_df = pd.read_sql(cast_query, con=engine)
cast_df_sorted = cast_df.sort_values("num_movies", ascending=False)

st.markdown("<h2 style='text-align: center;'> Top 20 Actors/Actresses with most movies </h2>",
            unsafe_allow_html=True)
chart = (
    alt.Chart(cast_df_sorted)
    .mark_bar()
    .encode(
        x=alt.X('cast_name', sort=None, title='Cast'),
        y=alt.Y('num_movies', title='Number of Movies'),
    )
)
st.altair_chart(chart, use_container_width=True)

genre_df = pd.read_sql(genre_query, con=engine)
genre_df['year'] = genre_df['year'].astype(int).astype(str)

st.markdown("<h2 style='text-align: center;'> Rating Per Genre </h2>",
            unsafe_allow_html=True)

all_genres = sorted(genre_df['genre_name'].unique())
default_genres = all_genres[:4]

selected_genres = st.multiselect(
    "Select genres to display",
    options=all_genres,
    default=default_genres
)

genre_filtered = genre_df[genre_df['genre_name'].isin(selected_genres)]
genre_pivot = genre_filtered.pivot(
    index='year', columns='genre_name', values='avg_rating')

st.line_chart(genre_pivot, x_label="Year", y_label="Average Rating")

scatter_df = pd.read_sql(budget_rating_query, con=engine)
st.markdown("<h2 style='text-align: center;'> Relation between Budget and Rating </h2>",
            unsafe_allow_html=True)
st.scatter_chart(scatter_df, x='budget', y='vote_average')
