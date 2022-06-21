from unittest import expectedFailure
from google.cloud import storage
import pandas as pd
import gcp_auth
from logger import logger,report
import config
from datetime import datetime

# get current date time
now = datetime.now()

now_str = now.strftime("%Y%m%d%H%M5S")

def get_csv_gcs(bucket_name, file_name):
    """Read csv from google cloud storage bucket."""
    
    csv_data = pd.read_csv('gs://' + bucket_name + '/' + file_name, encoding='utf-8')   

    return csv_data

def list_files_gcs(bucket_name,folder_name):
    """List all the blobs in the bucket folder."""
    
    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)

    file_names = []

    for blob in blobs:
        if blob.name.endswith('.csv'):
            # print(blob.name)
            file_names.append(blob.name)
    
    return file_names

def inspect_csv(bucket_name, file_name):
    """Load and inspect csv files from google cloud storage bucket."""
    logger.info(f"Start inspecting file: {file_name}" )
    try:
        # read csv file from gcs bucket
        csv_pd = get_csv_gcs(bucket_name,file_name)

        # write detailed information into txt file
        report.write("------------------------------------------------------------\n")
        report.write(f"Start inspecting file: {file_name} at {now_str}\n")        
        report.write(f"Total row count: {str(len(csv_pd))}\n")        
        report.write(f"Top 5 rows:\n {csv_pd.head()}\n")
        report.write(f"Columns with data types:\n{dict(csv_pd.dtypes)}\n")
        report.write(f"Check null values for each column:\n{csv_pd.isnull().sum()}\n")
        report.write(f"Summary :\n{csv_pd.describe()}\n")        
        report.write(f"End of inspecting file: {file_name}\n")
        report.write("------------------------------------------------------------\n")

        logger.info(f"Finish inspecting file: {file_name}")
        return csv_pd 

    except:
        # write error msg into log file
        logger.exception(f'Error occurred when inspecting file {file_name}.')      


def __name__():
    bucket_name = config.bucket_name
    nmi_file = config.nmi_file
    consumption_folder = config.consumption_folder

    # load and inspect nmi_info
    nmi_info = inspect_csv(bucket_name,nmi_file)

    # load and inspect consumption files
    consumption_files = list_files_gcs(bucket_name,consumption_folder)
    for consumption_file in consumption_files:        
        consumption_data = inspect_csv(bucket_name,consumption_file)

