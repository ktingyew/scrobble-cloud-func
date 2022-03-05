import logging
import pandas as pd
import os
from google.cloud import bigquery as bq

bq_client = bq.Client()

PROJECT_ID = os.environ['PROJECT_ID']
DATASET_ID = os.environ['DATASET_ID']
TABLE_ID = os.environ['TABLE_ID']

TABLE_REF_STR: str = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

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
tbl = bq.Table(TABLE_REF_STR, schema=schema) 

# Logging
logger = logging.getLogger("main.bq")
logger.debug(TABLE_REF_STR)

def get_latest_date(
) -> str :
    query = f"""SELECT * FROM `{TABLE_REF_STR}` WHERE `Datetime_n`=(SELECT MAX(`Datetime_n`) FROM `{TABLE_REF_STR}`)"""

    query_job = bq_client.query(query)
    df = query_job.result().to_dataframe()

    log_str = df.to_json(date_format='iso', orient='records', lines=True).rstrip('\n')
    logger.debug(f"Latest record obtained from BigQuery: {log_str}")

    dt_str = str(df['Datetime_n'][0])
    return dt_str


def append_to_bq(df: pd.DataFrame) -> None:

    BIGQUERY_COLUMN_NAMES = ['Title', 'Artist', 'Album', 'Datetime', 'Title_c', 'Artist_c', 'Datetime_n']

    # Reorder `append`'s order of columns to match exactly that of bq's
    df = df[BIGQUERY_COLUMN_NAMES]

    # Convert col type to one that is compatible with bq
    df['Datetime_n'] = pd.to_datetime(df['Datetime_n'])

    bq_client.load_table_from_dataframe(
        dataframe=df, 
        destination=TABLE_REF_STR,
        job_config=bq.job.LoadJobConfig(write_disposition="WRITE_APPEND")
    )
    logger.info(f"Successfully appended to {TABLE_REF_STR}")

