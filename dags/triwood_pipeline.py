from datetime import datetime, timedelta
from airflow.sdk import TaskGroup
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow import DAG
import sys
import os

# Add project root to sys.path BEFORE any imports
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


default_args = {
    'owner': 'matina',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
}


def choose_load_mode(**kwargs):
    """Branch between full and incremental load.
    Trigger via UI: Trigger DAG w/ config -> {"load_mode": "incremental"}
    Default (no config): full load
    """
    dag_run = kwargs.get('dag_run')
    conf = getattr(dag_run, 'conf', None) if dag_run else None

    print(f"DEBUG: dag_run={dag_run}")
    print(f"DEBUG: conf={conf}")
    print(f"DEBUG: conf type={type(conf)}")

    mode = 'full'
    if conf:
        if isinstance(conf, dict):
            mode = conf.get('load_mode', 'full')
        else:
            # Try converting to dict
            try:
                mode = dict(conf).get('load_mode', 'full')
            except Exception as e:
                print(f"DEBUG: conf conversion failed: {e}")
                mode = 'full'

    print(f"DEBUG: selected mode={mode}")

    if mode == 'incremental':
        return 'transform_load_incremental'
    return 'transform_and_load'


def run_transform_and_load():
    from src.pipeline.transform import load_movie_details, create_dataframes
    from src.pipeline.load import load_to_postgres
    all_movie_details = load_movie_details()
    dfs = create_dataframes(all_movie_details)
    load_to_postgres(*dfs)


def run_transform_and_load_incremental():
    from src.pipeline.load_incremental import load_incrementally
    load_incrementally()


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
            bash_command='uv run src/pipeline/ingest_raw_data.py',
            cwd=_PROJECT_ROOT
        )
        filter_movies = BashOperator(
            task_id='filter_movies',
            bash_command='uv run src/pipeline/filter_movies.py',
            cwd=_PROJECT_ROOT
        )
        ingest_details = BashOperator(
            task_id='ingest_details',
            bash_command='uv run src/pipeline/ingest_details.py',
            cwd=_PROJECT_ROOT
        )
        ingest_raw >> filter_movies >> ingest_details

    choose_mode = BranchPythonOperator(
        task_id='choose_load_mode',
        python_callable=choose_load_mode,
    )

    transform_load_task = PythonOperator(
        task_id='transform_and_load',
        python_callable=run_transform_and_load
    )

    transform_load_incremental_task = PythonOperator(
        task_id='transform_load_incremental',
        python_callable=run_transform_and_load_incremental
    )

    extract_group >> choose_mode >> [
        transform_load_task, transform_load_incremental_task]
