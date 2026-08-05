from sqlalchemy import create_engine, URL
from sqlalchemy.types import INTEGER, DateTime, BIGINT
from logger_config import get_logger
import os
from dotenv import load_dotenv
from quality import check_no_duplicate_movie_ids, check_budget_non_negative, check_vote_average_range

logger = get_logger(__name__)

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_DB=os.getenv('POSTGRES_DB')

url_object = URL.create(
    "postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_DB_HOST,
    database=POSTGRES_DB
)
engine = create_engine(url_object)

def load_to_postgres(dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df):
    check_no_duplicate_movie_ids(dim_movies_df)
    check_budget_non_negative(fact_movies_df)
    check_vote_average_range(fact_movies_df)

    dtype_dict = {
        'release_date': DateTime(),
        'revenue': BIGINT(),
        'runtime': INTEGER(),
        'budget': BIGINT()
    }

    tables = [
        (dim_movies_df, 'dim_movies',None),
        (dim_genres_df, 'dim_genres',None),
        (dim_cast_df, 'dim_cast',None),
        (bridge_genres_df,'bridge_genres',None),
        (bridge_cast_df,'bridge_cast', None)
    ]
    for df, table_name, dtype in tables:
        df.to_sql(name=table_name, con=engine,if_exists='replace', index=False)
        logger.info(f"Loaded {len(df)} rows into '{table_name}' table.")


    fact_movies_df.to_sql(name='fact_movies', con=engine,if_exists='replace', index=False, dtype=dtype_dict)
    logger.info(f"Loaded {len(fact_movies_df)} rows into 'fact_movies' table.")

if __name__ == "__main__":
    from transform import load_movie_details, create_dataframes

    logger.info("Starting data load pipeline...")

    all_movie_details = load_movie_details()
    dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df = create_dataframes(all_movie_details)
    load_to_postgres(dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df)

    logger.info("Pipeline completed successfully.")