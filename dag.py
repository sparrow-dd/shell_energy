from __future__ import print_function

import datetime

from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
import inspect_data
import validate_transform_data
import upload_bq

default_dag_args = {
    # Set up start_date when a DAG is valid
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    'start_date': datetime.datetime(2022, 6, 21),
}

# Define a DAG of tasks
with models.DAG(
        'shell_engergy_de',
        # runs every day
        schedule_interval=datetime.timedelta(days=1),
        # no schecule
        # schedule_interval=None,
        default_args=default_dag_args) as dag:

    # run inspect_data.py
    step_1_inspect_data = python_operator.PythonOperator(
        task_id='step_1_inspect_data',
        python_callable=inspect_data.__name__())

    # run upload_bq.py
    step_2_upload_bq = python_operator.PythonOperator(
        task_id='step_2_upload_bq',
        python_callable=upload_bq.__name__())    
    

    # Define the order in which the tasks complete by using the >> and <<
    # operators. In this example, hello_python executes before goodbye_bash.
    step_1_inspect_data >> step_2_upload_bq