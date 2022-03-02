import logging
import pandas as pd
import os
from google.cloud import bigquery as bq

PROJECT_ID = os.environ['PROJECT_ID']
DATASET_ID = os.environ['DATASET_ID']
TABLE_ID = os.environ['TABLE_ID']

logger = logging.getLogger("main.bq_local")

bq_client = bq.Client()
logger.info(f"BigQuery. Successfully authenticated")

ds_ref = bq.dataset.DatasetReference(PROJECT_ID, DATASET_ID) 
tbl_ref = bq.table.TableReference(ds_ref, TABLE_ID) 

fields = "Title:STRING,Artist:STRING,Album:STRING,Datetime:STRING," + \
    "Title_c:STRING,Artist_c:STRING,Datetime_n:DATETIME"

schema = [
    bq.SchemaField(
        name=f.split(':')[0], 
        field_type=f.split(':')[1], 
        mode='NULLABLE'
    ) 
    for f in fields.split(',')
]

# initialise table with schema using its (tbl) ref
tbl = bq.Table(tbl_ref, schema=schema) 
bq_client.delete_table(tbl, not_found_ok=True) # Truncate the table
# set optional parameter exists_ok=True to ignore error of table 
# already existing
bq_client.create_table(tbl) 

def upload_to_bq(df: pd.DataFrame):
    # schema in bq is DATETIME; requires this to be in pd's datetime format
    df['Datetime_n'] = pd.to_datetime(df['Datetime_n']) 
    bq_client.load_table_from_dataframe(df, tbl_ref)
    logger.info(f"load_table_from_dataframe to {tbl_ref} successful")
