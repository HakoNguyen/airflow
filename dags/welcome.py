from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

def print_welcome():
    print("Welcome to Airflow!")

def print_date():
    print("Today is {}".format(datetime.today().date()))

def print_random_quote():
    response = requests.get("https://api.quotable.io/random", verify=False)
    quote = response.json()["content"]
    print('Quote of the day: "{}"'.format(quote))

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime.now() - timedelta(days=1),
}

with DAG(
    dag_id="first_dag",
    default_args=default_args,
    schedule="0 23 * * *",  # chạy mỗi ngày lúc 23h
    catchup=False,
    tags=["example"],
) as dag:

    print_welcome_task = PythonOperator(
        task_id="print_welcome",
        python_callable=print_welcome,
    )

    print_date_task = PythonOperator(
        task_id="print_date",
        python_callable=print_date,
    )

    print_random_quote_task = PythonOperator(
        task_id="print_random_quote",
        python_callable=print_random_quote,
    )

    # Thiết lập thứ tự chạy
    print_welcome_task >> print_date_task >> print_random_quote_task
