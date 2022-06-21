import unittest
import pandas as pd
import config
from datetime import datetime
import validate_transform_data 
import inspect_data

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
    tc_files = [tc01_file, tc02_file, tc03_file,tc04_file,tc05_file]
    nmi_file = config.nmi_file


    # set up test cases
    def setUp(self):
        # set up data and validate/transform instance
        self.tc01_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc01_file)
        self.tc01_val = validate_transform_data.ValidateTransformData(self.tc01_data, self.tc01_file)      
        self.tc02_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc02_file)
        self.tc02_val = validate_transform_data.ValidateTransformData(self.tc02_data, self.tc02_file)   
        self.tc03_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc03_file)
        self.tc03_val = validate_transform_data.ValidateTransformData(self.tc03_data, self.tc03_file)   
        self.tc04_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc04_file)
        self.tc04_val = validate_transform_data.ValidateTransformData(self.tc04_data, self.tc04_file)   
        self.tc05_data = inspect_data.get_csv_gcs(self.bucket_name, self.tc05_file)
        self.tc05_val = validate_transform_data.ValidateTransformData(self.tc05_data, self.tc05_file) 
        
        # set up nmi info                 
        self.nmi_info = inspect_data.get_csv_gcs(self.bucket_name, self.nmi_file)
        
        # set up interval
        self.tc01_interval = validate_transform_data.get_interval(self.nmi_info,self.tc_folder,self.tc01_file)
        self.tc02_interval = validate_transform_data.get_interval(self.nmi_info,self.tc_folder,self.tc02_file)
        self.tc03_interval = validate_transform_data.get_interval(self.nmi_info,self.tc_folder,self.tc03_file)
        self.tc04_interval = validate_transform_data.get_interval(self.nmi_info,self.tc_folder,self.tc04_file)
        self.tc05_interval = validate_transform_data.get_interval(self.nmi_info,self.tc_folder,self.tc05_file)

    # test str_to_dt
    # check if the converted value is datetime type
    def test_01_str_to_dt(self):
        str_1 = '2017-10-01 04:00:00'
        dt_1 = validate_transform_data.str_to_dt(str_1)  
        str_2 = '01/10/2017 00:00:00'
        dt_2 = validate_transform_data.str_to_dt(str_2)         
        self.assertTrue(isinstance(dt_1,datetime))
        self.assertTrue(isinstance(dt_2,datetime))

    # test str_to_dt
    # check intervals: 15, 15, 30, 30, 30
    def test_02_get_interval(self):       
        self.assertEqual(self.tc01_interval,15)
        self.assertEqual(self.tc02_interval,15)
        self.assertEqual(self.tc03_interval,30)
        self.assertEqual(self.tc04_interval,30)
        self.assertEqual(self.tc05_interval,30)

    # test validate_columns  
    # true when expected_columns = ['AESTTime','Quantity','Unit'], otherwise false
    def test_03_validate_columns(self):
        self.assertTrue(self.tc01_val.validate_columns(expected_columns = ['AESTTime','Quantity','Unit']))
        self.assertFalse(self.tc02_val.validate_columns(expected_columns = ['AESTTime','Unit']))
        self.assertTrue(self.tc03_val.validate_columns(expected_columns = ['AESTTime','Quantity','Unit']))
        self.assertFalse(self.tc04_val.validate_columns(expected_columns = ['AESTTime','Quantity']))  
        self.assertTrue(self.tc05_val.validate_columns(expected_columns = ['AESTTime','Quantity','Unit']))    

    # test remove_duplicates
    # check length before and after removing duplicates
    # tc_03 should be different, others should be same
    def test_04_remove_duplicates(self):
        # get length before and after removing duplicates
        lb_01 = len(self.tc01_val.data) 
        self.tc01_val.remove_duplicates()
        la_01 = len(self.tc01_val.data)

        lb_03 = len(self.tc03_val.data) 
        self.tc03_val.remove_duplicates()
        la_03 = len(self.tc03_val.data)
        # compare length before and after
        self.assertEqual(lb_01,la_01)
        self.assertGreater(lb_03,la_03)

    # test process_AESTTime
    # check if output is expected (count_convert, count_fillna, count_invalid_removal, count_incorrect_interval)
    def test_05_process_AESTTime(self):
        result_01 = self.tc01_val.process_AESTTime(self.tc01_interval)
        result_02 = self.tc02_val.process_AESTTime(self.tc02_interval)
        result_03 = self.tc03_val.process_AESTTime(self.tc03_interval)
        result_04 = self.tc04_val.process_AESTTime(self.tc04_interval)
        result_05 = self.tc05_val.process_AESTTime(self.tc05_interval)
        self.assertEqual(result_01,(12, 0, 0, 0))
        self.assertEqual(result_02,(21, 0, 0, 2))
        self.assertEqual(result_03,(20, 0, 0, 2))
        self.assertEqual(result_04,(14, 5, 0, 0))
        self.assertEqual(result_05,(18, 1, 1, 0))

    # test process_AESTTime
    # check if output is expected (count_convert, count_fillna, count_invalid_removal, count_incorrect_interval)
    def test_06_process_Quantity_Unit(self):
        result_01 = self.tc01_val.process_Quantity_Unit()
        result_02 = self.tc02_val.process_Quantity_Unit()
        result_03 = self.tc03_val.process_Quantity_Unit()
        result_04 = self.tc04_val.process_Quantity_Unit()
        result_05 = self.tc05_val.process_Quantity_Unit()
        self.assertEqual(result_01,(0, 0))
        self.assertEqual(result_02,(0, 0))
        self.assertEqual(result_03,(0, 0))
        self.assertEqual(result_04,(1, 1))
        self.assertEqual(result_05,(1, 0))

    # test process_bundle
    # check if all df have all values populated and data type is correct.
    def test_07_process_bundle(self):
        nmi_info,consumption_files = validate_transform_data.process_bundle(self.bucket_name,self.nmi_file,self.tc_folder) 
        print(consumption_files)
        self.assertEqual(nmi_info.isnull().sum().sum(),0)
        self.assertEqual(consumption_files['NMIA1'].isnull().sum().sum(),0)
        self.assertEqual(consumption_files['NMIA2'].isnull().sum().sum(),0)
        self.assertEqual(consumption_files['NMIM1'].isnull().sum().sum(),0)
        self.assertEqual(consumption_files['NMIS2'].isnull().sum().sum(),0)
        self.assertEqual(consumption_files['NMIS3'].isnull().sum().sum(),0)

if __name__ == '__main__':
    unittest.main()