from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import sys
from os.path import expanduser,join as osjoin

with DAG('twitter_followers',default_args={'retries': 1,'owner':'blunt10k'},description='Collect Twitter followers',
schedule_interval='*/15 * * * *',catchup=False,tags=['twitter'],
start_date=pendulum.datetime(2022, 10, 28, tz="UTC")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','twitter_followers'))
    sys.path.insert(0,code_directory)

    from followers import collect

    extract_op = PythonOperator(task_id = 'extract',python_callable=collect)

    extract_op