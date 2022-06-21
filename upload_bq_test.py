from google.cloud import bigquery
import unittest
import config
import upload_bq
import inspect_data 
import validate_transform_data

class TestValidateTransformData(unittest.TestCase):
    """
        tc_01 all correct
        tc_02 missing rows
        tc_03 duplicate rows
        tc_04 missing values (time,quantity,unit)
        tc_05 invalid data types and values 
    """    
    # retrieve variables from config file
    bucket_name = config.bucket_name
    tc_folder = config.tc_folder 
    tc01_file = config.tc01_file
    tc02_file = config.tc02_file
    tc03_file = config.tc03_file
    tc04_file = config.tc04_file
    tc05_file = config.tc05_file
    nmi_file = config.nmi_file
    project_id = config.project_id
    dataset_id = config.dataset_id + "_TEST"
    # test upload_bq
    # check if the converted value is datetime type
    def test_01_str_to_dt(self):
        bq_client = bigquery.Client()

        # load csv into df
        nmi_info = inspect_data.get_csv_gcs(self.bucket_name,self.nmi_file)
        tc01_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc01_file)      
        tc02_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc02_file)           
        tc03_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc03_file)
        tc04_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc04_file)
        tc05_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc05_file) 
        
        # load df to bigquery
        upload_bq.load_df_to_bq(bq_client, nmi_info,self.project_id,self.dataset_id, table_name="nmi_info", job_config=upload_bq.job_config_nmi)
        upload_bq.load_df_to_bq(bq_client, tc01_data,self.project_id,self.dataset_id, table_name="tc01_data", job_config=upload_bq.job_config_comsumption)
        upload_bq.load_df_to_bq(bq_client, tc02_data,self.project_id,self.dataset_id, table_name="tc02_data", job_config=upload_bq.job_config_comsumption)
        upload_bq.load_df_to_bq(bq_client, tc03_data,self.project_id,self.dataset_id, table_name="tc03_data", job_config=upload_bq.job_config_comsumption)
        upload_bq.load_df_to_bq(bq_client, tc04_data,self.project_id,self.dataset_id, table_name="tc04_data", job_config=upload_bq.job_config_comsumption)
        upload_bq.load_df_to_bq(bq_client, tc05_data,self.project_id,self.dataset_id, table_name="tc05_data", job_config=upload_bq.job_config_comsumption)

        # check table stats
        result_nmi = upload_bq.load_df_to_bq(bq_client, nmi_info,self.project_id,self.dataset_id, table_name="nmi_info", job_config=upload_bq.job_config_nmi)
        result_01 = upload_bq.load_df_to_bq(bq_client, tc01_data,self.project_id,self.dataset_id, table_name="tc01_data", job_config=upload_bq.job_config_comsumption)
        result_02 = upload_bq.load_df_to_bq(bq_client, tc02_data,self.project_id,self.dataset_id, table_name="tc02_data", job_config=upload_bq.job_config_comsumption)
        result_03 = upload_bq.load_df_to_bq(bq_client, tc03_data,self.project_id,self.dataset_id, table_name="tc03_data", job_config=upload_bq.job_config_comsumption)
        result_04 = upload_bq.load_df_to_bq(bq_client, tc04_data,self.project_id,self.dataset_id, table_name="tc04_data", job_config=upload_bq.job_config_comsumption)
        result_05 = upload_bq.load_df_to_bq(bq_client, tc05_data,self.project_id,self.dataset_id, table_name="tc05_data", job_config=upload_bq.job_config_comsumption)
        
        self.assertEqual(result_nmi,(12,3,"our-highway-353804.NMI.nmi_info"))
        self.assertEqual(result_01,(12,3,"our-highway-353804.NMI.tc01_data"))
        self.assertEqual(result_02,(21,3,"our-highway-353804.NMI.tc02_data"))
        self.assertEqual(result_03,(20,3,"our-highway-353804.NMI.tc03_data"))
        self.assertEqual(result_04,(19,3,"our-highway-353804.NMI.tc04_data"))
        self.assertEqual(result_05,(20,3,"our-highway-353804.NMI.tc05_data"))

if __name__ == '__main__':
    unittest.main()       