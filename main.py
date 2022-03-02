import logging
import sys

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
fmtter = logging.Formatter(
    "[%(asctime)s]| %(levelname)8s| %(name)20s| %(message)s", 
    "%Y-%m-%d %H:%M:%S")
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(fmtter)
stdout_handler.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)

def main(data, context):

    # Log context 
    logger.debug(context)

    # Import from my modules
    from src.lastfm import get_df
    from src.gcs import (
        upload_to_bucket, 
        load_mapper_as_df_from_bucket,
        load_old_scrobbles_as_df_from_bucket
    )
    from src.bq import upload_to_bq
    from src.mapping import get_combined_mapped_scrobbles

    # Read df from last.fm API
    new = get_df()

    # Download latest scrobble from bucket, and load as df
    old = load_old_scrobbles_as_df_from_bucket()

    # Download mapper.csv from bucket, and load as df
    mapper = load_mapper_as_df_from_bucket()

    # Get combined df
    out = get_combined_mapped_scrobbles(new=new, old=old, mapper=mapper)

    # Only update/upload to Cloud if there new scrobbles (avoid waste network)
    if len(out) > len(old):

        # Save to temporary location, staging for uploading to GCS and BQ
        df_out_path: str = f"/tmp/scrobbles.jsonl"
        out.to_json(df_out_path, force_ascii=False, orient='records', lines=True)

        # Upload to GCS
        upload_to_bucket(df_out_path)

        # Upload to BQ
        upload_to_bq(out)
    else:
        logger.info("Nothing new to update. No uploading to GCS or BQ performed")

    logger.info("Function completed")

if __name__ == "__main__":

    main('data', 'context')