from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow import DAG
from datetime import datetime, timedelta
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


default_args = {
    'owner': 'matina',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


with DAG(
    dag_id='triwood_pipeline',
    default_args=default_args,
    description='ETL pipeline for Triwood movies',
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    with TaskGroup('extract_group') as extract_group:
        ingest_raw = BashOperator(
            task_id='ingest_raw',
            bash_command='uv run ingest_raw_data.py',
            cwd=PROJECT_ROOT
        )
        filter_movies = BashOperator(
            task_id='filter_movies',
            bash_command='uv run filter_movies.py',
            cwd=PROJECT_ROOT
        )
        ingest_details = BashOperator(
            task_id='ingest_details',
            bash_command='uv run ingest_details.py',
            cwd=PROJECT_ROOT
        )
        ingest_raw >> filter_movies >> ingest_details

    with TaskGroup('transform_load_group') as transform_load_group:
        def run_transform_and_load():
            from transform import load_movie_details, create_dataframes
            from load import load_to_postgres

            all_movie_details = load_movie_details()
            dim_movies_df, dim_genres_df, dim_cast_df, fact_movies_df, bridge_genres_df, bridge_cast_df = create_dataframes(
                all_movie_details)
            load_to_postgres(dim_movies_df, dim_genres_df, dim_cast_df,
                             fact_movies_df, bridge_genres_df, bridge_cast_df)

        transform_load_task = PythonOperator(
            task_id='transform_and_load',
            python_callable=run_transform_and_load
        )

    extract_group >> transform_load_group
