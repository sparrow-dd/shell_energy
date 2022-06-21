import unittest
import pandas as pd
import config
import inspect_data

class TestInspectData(unittest.TestCase):
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
    tc_files = [tc01_file, tc02_file, tc03_file,tc04_file,tc05_file]

    # test get_csv_gcs
    # all dataframes should not be empty
    def test_01_get_csv_gcs(self):
        tc01_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc01_file)      
        tc02_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc02_file)           
        tc03_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc03_file)
        tc04_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc04_file)
        tc05_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc05_file)                 
        self.assertFalse(tc01_data.empty)
        self.assertFalse(tc02_data.empty)
        self.assertFalse(tc03_data.empty)
        self.assertFalse(tc04_data.empty)
        self.assertFalse(tc05_data.empty)
    
    # test list_files_gcs
    # all test files should be listed
    def test_02_list_files_gcs(self):          
        tc = inspect_data.list_files_gcs(self.bucket_name,self.tc_folder)
        self.assertEqual(tc,self.tc_files)

    # test inspect_csv  
    # all dataframes should not be empty
    def test_03_inspect_csv(self):
        inspect_tc01_data = inspect_data.inspect_csv(self.bucket_name, self.tc01_file)      
        inspect_tc02_data = inspect_data.inspect_csv(self.bucket_name, self.tc02_file)           
        inspect_tc03_data = inspect_data.inspect_csv(self.bucket_name, self.tc03_file)
        inspect_tc04_data = inspect_data.inspect_csv(self.bucket_name, self.tc04_file)
        inspect_tc05_data = inspect_data.inspect_csv(self.bucket_name, self.tc05_file)
        self.assertFalse(inspect_tc01_data.empty)
        self.assertFalse(inspect_tc02_data.empty)
        self.assertFalse(inspect_tc03_data.empty)
        self.assertFalse(inspect_tc04_data.empty)
        self.assertFalse(inspect_tc05_data.empty)      


if __name__ == '__main__':
    unittest.main()
    
  