from logger_config import get_logger

logger = get_logger(__name__)

class DataQualityError(Exception):
    pass

def check_no_duplicate_movie_ids(df):
    duplicates = df['movie_id'].duplicated().sum()
    if duplicates >0:
        raise DataQualityError(f"Found {duplicates} duplicate movie_ids in dim_movies")
    logger.info("dim_movies: No duplicate movie_ids")

def check_budget_non_negative(df):
    invalid = df[df['budget'] < 0 ]
    if len(invalid) > 0:
        raise DataQualityError(f"{len(invalid)} movies have negative budget")
    logger.info("fact_movies: No negative budgets")

def check_vote_average_range(df):
    invalid = df[(df['vote_average']<0) | (df['vote_average'] >10)]
    if len(invalid) > 0:
        raise DataQualityError(f"{len(invalid)} movies have vote_average outside 0-10 range")
    logger.info("fact_movies: All vote_averages within valid range")