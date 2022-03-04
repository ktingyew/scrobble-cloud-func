# Imports the Google Cloud client library
import logging
from pathlib import Path
import pathlib

import pandas as pd

from google.cloud import storage
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob

# GCS_TARGET = Path(os.environ['GCS_TARGET'])

logger = logging.getLogger("main.gcs")

# Instantiates a client
# credentials = service_account.Credentials.from_service_account_file(GCS_TARGET)
# gcs_client = storage.Client(credentials=credentials)
gcs_client = storage.Client()
logger.info("GCS. Successfully authenticated")

# The name for the new bucket
bucket_name = "scrobbles-python"

my_bucket: Bucket = gcs_client.get_bucket(bucket_name)

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

