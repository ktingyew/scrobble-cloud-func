"""Module containing helper function relating to Google Cloud Storage"""
import logging
import pathlib
from pathlib import Path

from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
import pandas as pd

logger = logging.getLogger("main.gcs")


def load_mapper_as_df_from_bucket(
    bucket_name: str, blob_name: str = "mapper.csv"
) -> pd.DataFrame:
    """Download mapper.csv from bucket and store in /tmp."""
    # Init GCS Clint
    gcs_client = storage.Client()

    # Get Bucket obj
    my_bucket: Bucket = gcs_client.get_bucket(bucket_name)

    # Save path
    local_save_path: pathlib.Path = Path("/tmp") / blob_name

    blob: Blob = my_bucket.blob(blob_name)
    blob.download_to_filename(local_save_path)

    mapper: pd.DataFrame = pd.read_csv(local_save_path, sep="\t")  # tsv file
    logger.info(
        f"Retrieved {blob_name} from bucket={my_bucket} and loaded into DataFrame."
    )
    logger.debug(f"Size of mapper dataframe is {len(mapper)}")

    return mapper
