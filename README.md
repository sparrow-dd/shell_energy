# shell_energy

This project is done by using GCP (Google Cloud Platform).
### [Process Flow](https://miro.com/app/board/uXjVOr7xm6I=/?share_link_id=874788083498)

### Storage
Raw data files are loaded in to Google Cloud Storage Bucket 

### Issues identified during Input Data Inspection/Validation:
1. AESTTime field has two different formats (YYYY-MM-DD HH:MM:SS and DD/MM/YYYY HH:MM:SS)
2. AESTTime field has null values
3. Quantity filed has null values
4. NMIK4.csv is not in the list of nmi_info
5. NMIG2 is in the list but does not have a csv file 

### Data Processing:
1. Validate expected columns
2. Validate and convert data types (string to datetime)
3. Clean up invalid values and remove duplicates (if applicable)
4. Fill up null values (date based on interval, quantity default to 0, unit default to kWh)
5. Consolidate data (multiple files into one table with corresponding nmi)

### Folders:
1. #### Data contains all raw files and test files
2. #### logs contains log files produced by processing scripts
3. #### reports contains output file produced by inspect_data.py

### Scripts:
1. #### config.py contains the list of config variables
2. #### gcp_auth.py authenticates service account for GCP project
3. #### service_account_key.json contains the service account key
4. #### logger.py is used to set up logging format
5. #### inspect_data.py is the script to inspect raw files
6. #### validate_transform_data.py is the script to validate and transform raw files
7. #### upload_bq.py is the script to upload dataframes into BigQuery tables
8. #### dag.py is used to schedule tasks
9. #### upload_dag.py is used to upload dag.py into Google Cloud Composer Airflow bucket

### Unittest scripts:
1. #### inspect_data_test.py is the test script for inspect_data.py
2. #### validate_transform_data_test.py is the test script for validate_transform_data.py
3. #### upload_bq_test.py is the test script for upload_bq.py


### Other files:
1. #### requirements.txt contains the list of libraries in the env
2. #### README.md contains detailed information about this project
3. #### Consumption Distribution.twb contains a Tableau workbook for visualisation
![image](https://user-images.githubusercontent.com/99944247/174701386-6ceb1e7b-068e-4cb8-966b-716522d9885f.png)
