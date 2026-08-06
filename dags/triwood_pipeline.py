from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.sdk import TaskGroup
from datetime import datetime, timedelta
import os
import sys

default_args = {
    'owner': 'matina',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
}


def choose_load_mode(**kwargs):
    """Branch between full and incremental load.
    Trigger with config: {"load_mode": "incremental"} for incremental.
    Default is full load.
    """
    mode = kwargs['dag_run'].conf.get('load_mode', 'full')
    if mode == 'incremental':
        return 'transform_load_incremental'
    return 'transform_and_load'


with DAG(
    dag_id='triwood_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
) as dag:

    with TaskGroup('extract_group') as extract_group:
        ingest_raw = BashOperator(
            task_id='ingest_raw',
            bash_command='uv run src/pipeline/ingest_raw_data.py'
        )
        filter_movies = BashOperator(
            task_id='filter_movies',
            bash_command='uv run src/pipeline/filter_movies.py'
        )
        ingest_details = BashOperator(
            task_id='ingest_details',
            bash_command='uv run src/pipeline/ingest_details.py'
        )
        ingest_raw >> filter_movies >> ingest_details

    choose_mode = BranchPythonOperator(
        task_id='choose_load_mode',
        python_callable=choose_load_mode,
    )

    def run_transform_and_load():
        import sys
        import os
        sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        from src.pipeline.transform import load_movie_details, create_dataframes
        from src.pipeline.load import load_to_postgres
        all_movie_details = load_movie_details()
        dfs = create_dataframes(all_movie_details)
        load_to_postgres(*dfs)

    transform_load_task = PythonOperator(
        task_id='transform_and_load',
        python_callable=run_transform_and_load
    )

    def run_transform_and_load_incremental():
        import sys
        import os
        sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        from src.pipeline.load_incremental import load_incrementally
        load_incrementally()

    transform_load_incremental_task = PythonOperator(
        task_id='transform_load_incremental',
        python_callable=run_transform_and_load_incremental
    )

    extract_group >> choose_mode >> [
        transform_load_task, transform_load_incremental_task]
