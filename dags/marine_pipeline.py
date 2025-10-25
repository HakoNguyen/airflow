from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("/opt/airflow/dags/src/marineV")

INGEST_SCRIPT = BASE_DIR / "run_ingest.py"
PROCESS_SCRIPT = BASE_DIR / "process.py"
LOAD_S3_SCRIPT = BASE_DIR / "load_s3.py"
LOAD_POSTGRES_SCRIPT = BASE_DIR / "load_postgres.py"

def run_script(scrip_path, *args):
    print(f"Running {scrip_path.name} with args: {args}")
    result = subprocess.run([sys.executable, str(scrip_path), *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error in {scrip_path.name}: {result.stderr}')
        raise Exception(result.stderr)
    print(result.stdout)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    default_args = default_args,
    dag_id = 'marine_pipline',
    description = 'Full marine data ETL: ingest → process → upload S3 → load Postgres',
    schedule = "0 6 * * *",
    start_date = datetime(2025, 10, 1),
    catchup = False,
    max_active_runs = 1,
    tags = ['marine', 'ETL', 'S3']
) as dag:
    
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Task 1 - ingest data
    ingest_task = PythonOperator(
        task_id = 'ingest_data',
        python_callable = run_script,
        op_args = [INGEST_SCRIPT],
    )

    # Task 2 - process data 
    process_task = PythonOperator(
        task_id = 'process_data',
        python_callable = run_script, 
        op_args = [PROCESS_SCRIPT, '--date', date_str],
    )

    # Task 3 - upload to S3
    upload_s3_task = PythonOperator(
        task_id = 'upload_to_s3',
        python_callable = run_script,
        op_args = [LOAD_S3_SCRIPT, date_str],
    )

    # Task 4 - upload to supabase (postgres cloud)
    load_postgres_task = PythonOperator(
        task_id = "load_to_postgres",
        python_callable = run_script,
        op_args = [LOAD_POSTGRES_SCRIPT, date_str]
    )

    ingest_task >> process_task >> upload_s3_task >> load_postgres_task