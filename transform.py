import json
import logging
import os
import pandas as pd
from logger_config import get_logger

logger = get_logger(__name__)

languages = ["en", "hi", "ko"]


def load_movie_details():
    all_movie_details = []
    for lang in languages:
        file_name = f"details/{lang}_movie_details.json"
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                movie_details = json.load(file)
            all_movie_details.extend(movie_details)
            logger.info(f"Loaded {len(movie_details)} movies.")

        except FileNotFoundError:
            logger.error(
                f"Error: The file {lang}_movie_details.json was not found.")

    logger.info(f"\n Total loaded  movies: {len(all_movie_details)}.")
    return all_movie_details


def create_fact_movies(all_movie_details):
    fact_movies = []
    for movie in all_movie_details:
        temp_dict = {
            'movie_id': movie['movie_id'],
            'release_date': movie['release_date'],
            'popularity': movie['popularity'],
            'revenue': movie['revenue'],
            'runtime': movie['runtime'],
            'vote_average': movie['vote_average'],
            'vote_count': movie['vote_count'],
            'budget': movie['budget'],
        }
        fact_movies.append(temp_dict)
    return fact_movies


def create_dim_movies(all_movie_details):
    dim_movies = []
    for movie in all_movie_details:
        temp_dict = {
            'movie_id': movie['movie_id'],
            'movie_title': movie['movie_title'],
            'original_language': movie['original_language'],
        }
        dim_movies.append(temp_dict)
    df = pd.DataFrame(dim_movies)
    df = df.drop_duplicates(subset=['movie_id'],keep='first')
    return df.to_dict('records')

def create_dim_genres(all_movie_details):
    all_genre_names = []
    dim_genres = []
    for movie in all_movie_details:
        for genre in movie['genres']:
            all_genre_names.append(genre)

    unique_genres = set(all_genre_names)
    for genre_id, genre_name in enumerate(unique_genres, start=1):
        temp_dict = {
            'genre_id': genre_id,
            'genre_name': genre_name
        }
        dim_genres.append(temp_dict)
    return dim_genres


def create_bridge_genres(all_movie_details, dim_genres):
    bridge_genres = []
    genre_lookup = {g['genre_name']: g['genre_id'] for g in dim_genres}
    for movie in all_movie_details:
        for genre_name in movie['genres']:
            temp_dict = {'movie_id': movie['movie_id'],
                         'genre_id': genre_lookup[genre_name]}
            bridge_genres.append(temp_dict)
    return bridge_genres


def create_dim_cast(all_movie_details):
    all_cast_names = []
    dim_cast = []
    for movie in all_movie_details:
        for cast in movie['cast']:
            all_cast_names.append(cast)

    unique_cast = set(all_cast_names)
    for cast_id, cast_name in enumerate(unique_cast, start=1):
        temp_dict = {
            'cast_id': cast_id,
            'cast_name': cast_name
        }
        dim_cast.append(temp_dict)
    return dim_cast


def create_bridge_cast(all_movie_details, dim_cast):
    bridge_cast = []
    cast_lookup = {c['cast_name']: c['cast_id'] for c in dim_cast}
    for movie in all_movie_details:
        for cast_order, cast_name in enumerate(movie['cast'], start=1):
            temp_dict = {
                'movie_id': movie['movie_id'], 'cast_order': cast_order, 'cast_id': cast_lookup[cast_name]}
            bridge_cast.append(temp_dict)
    return bridge_cast


def check_nulls(df, table_name):
    count = df.isnull().sum()
    if count.sum() == 0:
        logger.info(f"{table_name}: No null values found.")
    else:
        logger.warning(f"{table_name} null counts:\n{count}")


def create_dataframes(all_movie_details):
    # build dimensions first because bridges need them for lookups
    dim_movies = create_dim_movies(all_movie_details)
    dim_genres = create_dim_genres(all_movie_details)
    dim_cast = create_dim_cast(all_movie_details)

    # build facts and bridges
    fact_movies = create_fact_movies(all_movie_details)

    bridge_genres = create_bridge_genres(all_movie_details, dim_genres)
    bridge_cast = create_bridge_cast(all_movie_details, dim_cast)

    # Convert to DataFrames
    dim_movies_df = pd.DataFrame(dim_movies)
    dim_genres_df = pd.DataFrame(dim_genres)
    dim_cast_df = pd.DataFrame(dim_cast)

    fact_movies_df = pd.DataFrame(fact_movies)

    bridge_genres_df = pd.DataFrame(bridge_genres)
    bridge_cast_df = pd.DataFrame(bridge_cast)

    # Type fixes and null handling
    fact_movies_df['release_date'] = pd.to_datetime(
        fact_movies_df['release_date'])
    fact_movies_df['revenue'] = fact_movies_df['revenue'].replace(
        0, pd.NA).astype('Int64')
    fact_movies_df['runtime'] = fact_movies_df['runtime'].replace(
        0, pd.NA).astype('Int64')
    fact_movies_df['budget'] = fact_movies_df['budget'].replace(
        0, pd.NA).astype('Int64')

    # vote_count stays as-is (int, 0 might be real)
    # popularity and vote_average stay float

    # Null checks
    check_nulls(dim_movies_df, "dim_movies")
    check_nulls(dim_genres_df, "dim_genres")
    check_nulls(dim_cast_df, "dim_cast")
    check_nulls(fact_movies_df, "fact_movies")
    check_nulls(bridge_genres_df, "bridge_genres")
    check_nulls(bridge_cast_df, "bridge_cast")

    return dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df
