"""Entry point of script."""
from datetime import datetime
import logging.config
import os

import pandas as pd
from pytz import timezone

from src.my_scrobble.bq import get_latest_date, append_to_bq
from src.my_scrobble.gcs import load_mapper_as_df_from_bucket
from src.my_scrobble.lastfm import get_df_lastfm
from src.my_scrobble.mapping import map_the_new, filter_lastfm_scrobbles

BUCKET_NAME = os.environ["BUCKET_NAME"]

PROJECT_ID = os.environ["PROJECT_ID"]
DATASET_ID = os.environ["DATASET_ID"]
TABLE_ID = os.environ["TABLE_ID"]
TABLE_REF_STR: str = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

SCROBBLE_RETRIEVE_COUNT: str = os.environ["SCROBBLE_RETRIEVE_COUNT"]
LASTFM_USERNAME = os.environ["LASTFM_USERNAME"]
LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]


class myFormatter(logging.Formatter):
    """Custom formatter for logger handler."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.converter = lambda *args: datetime.now(
            tz=timezone("Asia/Singapore")
        ).timetuple()


# Logging configuration using file
logging.config.fileConfig(fname="logging.ini", disable_existing_loggers=True)
logger = logging.getLogger("main")


def main(data, context) -> None:
    """Entry point."""
    # Log context
    logger.debug(context)

    # Get latest date from bq
    r: str = get_latest_date(TABLE_REF_STR)

    # Read df from last.fm API
    lastfm_df: pd.DataFrame = get_df_lastfm(
        lastfm_username=LASTFM_USERNAME,
        last_apikey=LASTFM_API_KEY,
        num_scrobs=int(SCROBBLE_RETRIEVE_COUNT),
    )

    # Filter new down to only contain new scrobbles not alr in bq
    new: pd.DataFrame = filter_lastfm_scrobbles(lastfm_df, r)

    # Upload to bq if there are one or more records
    if len(new) >= 1:

        # Download mapper.csv from bucket, and load as df
        mapper: pd.DataFrame = load_mapper_as_df_from_bucket(bucket_name=BUCKET_NAME)

        # Process new with mapper
        append: pd.DataFrame = map_the_new(new, mapper)

        # Append to table in bq
        append_to_bq(table_ref_str=TABLE_REF_STR, df=append)

    else:
        logger.info(f"No new songs scrobbled since date_string={r}")

    logger.info("Scrobble Update Cycle Completed")


if __name__ == "__main__":

    main("data", "context")
