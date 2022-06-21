
from fileinput import filename
from google.cloud import storage
import pandas as pd
import gcp_auth
import inspect_data
import config
from datetime import datetime
from datetime import timedelta
from logger import logger
import numpy as np


# class TransformData:
#     """Define a class to transform data."""

def str_to_dt(str):
    """Convert string to datetime object.
        Observed formats of datetime string is one of the below:
        YYYY-MM-DD HH:MM:SS        
        DD/MM/YYYY HH:MM:SS
        
    """    
    str_formats = ["%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M:%S"]
    # try to convert from one of the formats above
    for str_format in str_formats:        
        try: 
            dt_obj = datetime.strptime(str,str_format)            
            return dt_obj
        except:
            continue
    raise ValueError('no valid date format found.')

def get_interval(nmi_info,consumption_folder,consumption_file):
    """Get interval by looking up nmi in nmi_info."""
    # get nmi from consumption data file name
    nmi = consumption_file.replace(consumption_folder + '/', '').replace('.csv', '')
    # get interval for this nmi
    interval = nmi_info[nmi_info['Nmi'] == nmi]['Interval'].item()
    return interval

class ValidateTransformData:
    """Define a class to validate consumption data."""
    # define expected_columns
    expected_columns = ['AESTTime','Quantity','Unit']

    def __init__(self, data, file_name):
        """Define two properties."""
        self.data = data
        self.file_name = file_name

    def validate_columns(self,expected_columns):
        """Validate columns in consumption data."""        

        logger.info(f"Start validating columns in file: {self.file_name}")

        # check if the columns are the same as expected columns
        if list(self.data.columns) == expected_columns:
            logger.info(f"Columns are as expected: {expected_columns}")
            logger.info(f"Finish validating columns in file: {self.file_name}")
            return True  
        else:
            logger.error(f"Columns are {list(self.data.columns)}, not as expected columns {expected_columns}. Check source file {self.file_name}.")
            return False
    
    def remove_duplicates(self):
        """Check and remove duplicates."""

        logger.info(f"Start checking duplicates in file: {self.file_name}")
        
        # check if the dataframe has duplicate rows
        if not self.data.duplicated().empty:            
            logger.info(f"{len(self.data[self.data.duplicated()])} duplicated row(s) have been found.")
            logger.info(f"{len(self.data)} row(s) before dropping duplicates.")

            # drop duplicated rows and only keep one row for each duplicate pair 
            self.data.drop_duplicates(inplace=True, ignore_index=True)
            logger.info(f"{len(self.data)} row(s) after dropping duplicates.")

        else:
            logger.info(f"No duplicated row(s).")

        logger.info(f"Finish checking duplicates in file: {self.file_name}")

    def process_AESTTime(self,interval):
        """Validate and transform AESTTime."""
        
        # validate and transform AESTTime
        logger.info(f"Start processing AESTTime in file: {self.file_name}.")

        logger.info(f"Cleaning up values in AESTTime.")

        count_convert = 0
        count_fillna = 0
        count_invalid_removal = 0 
        count_incorrect_interval = 0

        # iterate row in df
        for i, row in self.data.iterrows():
            # check value in AESTTime 
            dt_str = self.data.at[i,"AESTTime"]
            continue_execution = True

            # when not None convert to datetime
            
            if pd.isna(dt_str) == False:            
                try:
                    dt = str_to_dt(dt_str)
                    self.data.at[i,"AESTTime"] = dt
                    count_convert +=1
                    continue_execution = False
                    
                except:
                    logger.exception(f"Couldn't parse {dt_str} to datetime at row index {i}. Try to replace invalid value to previous datetime plus interval.")
                
                if continue_execution:                    
                    try:            
                        self.data.at[i,"AESTTime"] = self.data.at[i-1,"AESTTime"] + timedelta(minutes = interval)
                        count_invalid_removal +=1
                    except:
                        logger.error(f"Error when trying to fill in AESTTime at row {i} with datetime from previous row plus interval.") 
            
            # when None fill in value from previous row plus interval
            else:
                try:                    
                    self.data.at[i,"AESTTime"] = self.data.at[i-1,"AESTTime"] + timedelta(minutes = interval)
                    count_fillna +=1
                    logger.info(f"Fill in AESTTime at row {i} with datetime from previous row plus interval {interval} minutes.") 
                except:
                    logger.error(f"Error when trying to fill in AESTTime at row {i} with datetime from previous row plus interval.") 
                
        logger.info(f"Finish cleaning up values in AESTTime.")
        
        # check if each row has correct interval after cleansing
        logger.info(f"Checking interval for AESTTime.")
        
        check_interval = self.data["AESTTime"].diff().apply(lambda x: x/np.timedelta64(1, 'm')).fillna(0).astype('int64')
        incorrect_interval = check_interval[check_interval != interval]

        if len(incorrect_interval) > 1:
            count_incorrect_interval = len(incorrect_interval)-1
            logger.error(f"{count_incorrect_interval} rows have incorrect interval.")
            logger.error(f"Row    Interval:\n {incorrect_interval}\n")    
        else:
            logger.info(f"All rows have correct interval {interval} minutes.")

        logger.info(f"Finish checking interval for AESTTime.")
        
        logger.info(f"Finish processing AESTTime in file: {self.file_name}: converted {count_convert} values; filled {count_fillna} blanks, removed {count_invalid_removal} invalid values, identified {count_incorrect_interval} incorrect intervals.")

        return  count_convert, count_fillna, count_invalid_removal, count_incorrect_interval

    def process_Quantity_Unit(self):
        """Validate and transform Quantity and Unit.
         Quantity default to 0.
         Unit default to kWh.        
        """        
        # validate and transform Quantity and Unit
        # default blank values to 0 for Quantity
        # default blank values to kWh for Unit
        logger.info(f"Start processing Quantity and Unit in file: {self.file_name}.")
        
        count_blank_quantity = 0 
        count_blank_unit = 0 

        for i, row in self.data.iterrows():
            # check value in Quantity 
            if pd.isna(self.data.at[i,"Quantity"]):
                self.data.at[i,"Quantity"] = 0
                count_blank_quantity +=1 
            if pd.isna(self.data.at[i,"Unit"]):
                self.data.at[i,"Unit"] = 'kWh'
                count_blank_unit +=1

        logger.info(f"Finish processing Quantity and Unit in file: {self.file_name}: {count_blank_quantity} invalid/blank Quantity values have been set to 0. {count_blank_unit} invalid/blank Unit values have been set to kwh.")
        
        return count_blank_quantity,count_blank_unit

def process_bundle(bucket_name,nmi_file,consumption_folder):
    # load nmi_info
    logger.info(f"Processing...{nmi_file}")
    nmi_info = inspect_data.get_csv_gcs(bucket_name,nmi_file)

    # load consumption files
    consumption_files = inspect_data.list_files_gcs(bucket_name,consumption_folder)
    logger.info(f"Processing...{consumption_files}")

    # processed_consumption_data = {}
    union = pd.DataFrame(columns =['Nmi','AESTTime','Quantity','Unit'])

    for consumption_file in consumption_files: 
        
        try:
            # when nmi is listed in the info file
            # ge nmi from file name
            nmi = consumption_file.replace(consumption_folder + '/', '').replace('.csv', '')   
            # print(nmi)        

            # get interval for this nmi
            interval = get_interval(nmi_info,consumption_folder,consumption_file)

            consumption_data = inspect_data.get_csv_gcs(bucket_name,consumption_file)
            logger.info("Processing...{consumption_file}")

            # initiate validate class
            val = ValidateTransformData(consumption_data,consumption_file)

            logger.info("Checking columns...{consumption_file}")
            # check columns output in log file     
            result = val.validate_columns(expected_columns = ['AESTTime','Quantity','Unit'])
            
            logger.info("It's {result} that columns are as expected.")

            logger.info(f"Removing duplicates...{consumption_file}")
            # remove duplicates
            val.remove_duplicates()

            logger.info(f"Processing AESTTime...{consumption_file}")
            # process AESTTime
            val.process_AESTTime(interval)

            logger.info(f"Processing Quantity and Unit...{consumption_file}")
            # process Quantity and Unit
            val.process_Quantity_Unit()
            
            # add column nmi
            
            val.data.insert(0,'Nmi',nmi)
            # append df to the list            
            # processed_consumption_data[nmi] = val.data
            
            # print(type(val.data))
            logger.info(f"Finish processing file {consumption_file}.")
            
            # combine all df together
            union = union.append(val.data)
        except:
            logger.exception(f"Nmi for {consumption_file} does not exist in nmi_info.")

    return nmi_info,union    

if __name__ == '__main__':

    bucket_name = config.bucket_name  
    nmi_file = config.nmi_file
    consumption_folder = config.consumption_folder 
    nmi_df,union_df = process_bundle(bucket_name,nmi_file,consumption_folder) 
    print("nmi_df:\n",nmi_df.info())
    print("union_df:\n",union_df.info())



