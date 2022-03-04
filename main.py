from datetime import datetime
import logging
import sys

from pytz import timezone

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
fmtter = logging.Formatter(
    fmt="%(asctime)s| %(levelname)8s| %(name)15s| %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S")
fmtter.converter = lambda *args: datetime.now(tz=timezone('Asia/Singapore')).timetuple()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(fmtter)
stdout_handler.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)

def main(data, context):

    # Log context 
    logger.debug(context)

    # Import from my modules
    from src.lastfm import get_df
    from src.gcs import load_mapper_as_df_from_bucket
    from src.bq import get_latest_date, append_to_bq
    from src.mapping import map_the_new, filter_new_scrobbles

    # Download mapper.csv from bucket, and load as df
    mapper = load_mapper_as_df_from_bucket()

    # Get latest date from bq
    r: str = get_latest_date()

    # Read df from last.fm API
    new = get_df(pages=1)

    # Filter new down to only contain new scrobbles not alr in bq
    new = filter_new_scrobbles(new, r)

    # Process new with mapper
    append = map_the_new(new, mapper)

    # Upload to bq if there are one or more records
    if len(append) >= 1:

        # Append to table in bq
        append_to_bq(append)

    else:
        logger.info(f"No new songs scrobbled since date_string={r}")

    logger.info("Scrobble Update Cycle Completed")

if __name__ == "__main__":

    main('data', 'context')

