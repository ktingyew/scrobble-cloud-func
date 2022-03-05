import logging
import os
from pathlib import Path
import pathlib

from google.cloud import storage
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob
import pandas as pd

gcs_client = storage.Client()

BUCKET_NAME = os.environ['BUCKET_NAME']

my_bucket: Bucket = gcs_client.get_bucket(BUCKET_NAME)

logger = logging.getLogger("main.gcs")

def load_mapper_as_df_from_bucket():
    # Download mapper.csv from bucket and store in /tmp

    blob_name: str = "mapper.csv"
    local_save_path: pathlib.Path = Path("/tmp") / blob_name

    blob: Blob = my_bucket.blob(blob_name)
    blob.download_to_filename(local_save_path)

    mapper = pd.read_csv(local_save_path, sep='\t') # tsv file
    logger.info(f"Retrieved {blob_name} from bucket={my_bucket} and loaded into DataFrame")
    logger.debug(f"Size of mapper dataframe is {len(mapper)}")

    return mapper

