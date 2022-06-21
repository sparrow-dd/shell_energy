import datetime

from google.cloud import bigquery
import pandas
import pytz
import config
import inspect_data
import validate_transform_data
from logger import logger

# retrieve project_id and dataset_id from config file
project_id = config.project_id
dataset_id = config.dataset_id

# define config for consumption data
job_config_comsumption = bigquery.LoadJobConfig(
    # Specify a schema
    schema=[
        # Specify data type of columns
        bigquery.SchemaField("Nmi", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("AESTTime", bigquery.enums.SqlTypeNames.DATETIME),
        bigquery.SchemaField("Quantity", bigquery.enums.SqlTypeNames.FLOAT64),
        bigquery.SchemaField("Unit", bigquery.enums.SqlTypeNames.STRING),
    ],
    # replaces the table with the loaded data
    write_disposition="WRITE_TRUNCATE",
)

# define config for nmi data
job_config_nmi = bigquery.LoadJobConfig(
    # Specify a schema
    schema=[
        # Specify data type of columns
        bigquery.SchemaField("Nmi", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("State", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("Interval", bigquery.enums.SqlTypeNames.INT64),
    ],
    # replaces the table with the loaded data
    write_disposition="WRITE_TRUNCATE",
)

def load_df_to_bq(client,dataframe,project_id,dataset_id,table_name,job_config):

    table_id= project_id + "." + dataset_id + "." + table_name
    # make API call to load dataframe to bigquery table
    job = client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)

    # wait for completion
    job.result()

    # get table stats via API request.
    table = client.get_table(table_id) 

    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
    return table.num_rows,len(table.schema),table_id

def __name__():
    # Construct a BigQuery client object
    bq_client = bigquery.Client()

    bucket_name = config.bucket_name  
    nmi_file = config.nmi_file
    consumption_folder = config.consumption_folder    

    # process bundle
    nmi_df, union_df = validate_transform_data.process_bundle(bucket_name,nmi_file,consumption_folder) 

    # load df to bigquery
    load_df_to_bq(bq_client, nmi_df,project_id,dataset_id,table_name="nmi_info", job_config=job_config_nmi)
    load_df_to_bq(bq_client, union_df,project_id,dataset_id, table_name='consumption', job_config=job_config_comsumption)
  

__name__()
