from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

def internet_check():
    r = requests.get("https://www.google.com")
    print(r.status_code)


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime.now() - timedelta(days=1),
}

with DAG(
    dag_id="internet_check",
    default_args=default_args,
    schedule="0 12 * * *",  
    catchup=False,
    tags=["example"],
) as dag:
    
    internet_check_task = PythonOperator(
        task_id="internet_check",
        python_callable=internet_check,
    )

    internet_check_task