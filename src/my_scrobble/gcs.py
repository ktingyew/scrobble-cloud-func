"""Module containing helper function relating to Google Cloud Storage."""
import logging
from pathlib import Path

from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
import pandas as pd

logger = logging.getLogger("main.gcs")


def load_mapper_as_df_from_bucket(
    bucket_name: str,
    blob_name: str = "mapper.csv",
    save_to_path: Path = Path("/tmp") / "mapper.csv",
) -> pd.DataFrame:
    """Download mapper.csv from bucket and return it as Pandas DataFrame.

    The "mapper" is used to translate raw Title and Artist tags from scrobbles into
        ones that are pre-defined.

    Args:
        bucket_name: Cloud Storage bucket name containing the mapper file.
        blob_name: Filename of mapper file in bucket `bucket_name`.
        save_to_path: Local path to save the mapper file downloaded from Cloud Storage.
    """
    # Init GCS Clint
    gcs_client = storage.Client()

    # Get Blob from Bucket
    my_bucket: Bucket = gcs_client.get_bucket(bucket_name)
    blob: Blob = my_bucket.blob(blob_name)

    # Download to save_to_path
    blob.download_to_filename(save_to_path)

    # Load as DataFrame
    mapper: pd.DataFrame = pd.read_csv(save_to_path, sep="\t")  # tsv file
    logger.info(
        f"Retrieved {blob_name} from bucket={my_bucket} and loaded into DataFrame."
    )
    logger.debug(f"Size of mapper dataframe is {len(mapper)}")

    return mapper
