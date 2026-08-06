import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from src.pipeline.logger_config import get_logger
from src.pipeline.transform import load_movie_details, create_dataframes
from src.pipeline.load import engine, load_to_postgres
from sqlalchemy import text



logger = get_logger(__name__)


def load_incrementally():
    """Load only movies not already present in dim_movies."""

    # 1. Check what's already in the database
    with engine.connect() as conn:
        result = conn.execute(text("SELECT movie_id FROM dim_movies"))
        existing_ids = {row[0] for row in result}

    logger.info(f"Found {len(existing_ids)} existing movies in database.")

    # 2. Transform all source data
    all_movie_details = load_movie_details()
    dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df = create_dataframes(
        all_movie_details)

    # 3. Filter to NEW movies only
    new_mask = ~dim_movies_df['movie_id'].isin(existing_ids)
    new_movie_ids = set(dim_movies_df.loc[new_mask, 'movie_id'])

    if len(new_movie_ids) == 0:
        logger.info("No new movies to load. Database is already up to date.")
        return

    logger.info(
        f"Found {len(new_movie_ids)} new movies to load incrementally.")

    # 4. Filter ALL dataframes to only new movies
    dim_movies_df = dim_movies_df[dim_movies_df['movie_id'].isin(
        new_movie_ids)]
    fact_movies_df = fact_movies_df[fact_movies_df['movie_id'].isin(
        new_movie_ids)]
    bridge_genres_df = bridge_genres_df[bridge_genres_df['movie_id'].isin(
        new_movie_ids)]
    bridge_cast_df = bridge_cast_df[bridge_cast_df['movie_id'].isin(
        new_movie_ids)]

    # 5. For dimensions (genres, cast), we also need to filter out existing ones
    #    to avoid unique constraint violations on genre_name / cast_name
    with engine.connect() as conn:
        existing_genres = {row[0] for row in conn.execute(
            text("SELECT genre_name FROM dim_genres"))}
        existing_cast = {row[0] for row in conn.execute(
            text("SELECT cast_name FROM dim_cast"))}

    dim_genres_df = dim_genres_df[~dim_genres_df['genre_name'].isin(
        existing_genres)]
    dim_cast_df = dim_cast_df[~dim_cast_df['cast_name'].isin(existing_cast)]

    # 6. Load only new data
    load_to_postgres(dim_movies_df, dim_genres_df, dim_cast_df,
                     fact_movies_df, bridge_genres_df, bridge_cast_df)
    logger.info(f"Incrementally loaded {len(new_movie_ids)} new movies.")


if __name__ == "__main__":
    load_incrementally()
