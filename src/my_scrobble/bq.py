"""BigQuery module."""
import logging

import pandas as pd
from google.cloud import bigquery as bq

# Logging
logger = logging.getLogger("main.bq")


def get_latest_date(table_ref_str: str) -> str:
    """Given a BQ table, find the latest date.

    Return datetime value as string.
    """
    bq_client = bq.Client()

    query = f"""SELECT * FROM `{table_ref_str}` \
        WHERE `Datetime_n`=(SELECT MAX(`Datetime_n`) FROM `{table_ref_str}`)"""

    query_job = bq_client.query(query)
    df = query_job.result().to_dataframe()

    log_str = df.to_json(date_format="iso", orient="records", lines=True).rstrip("\n")
    logger.debug(f"Latest record obtained from BigQuery: {log_str}")

    dt_str = str(df["Datetime_n"][0])

    return dt_str


def append_to_bq(table_ref_str: str, df: pd.DataFrame) -> None:
    """Append df rows to bq table."""
    bq_client = bq.Client()

    BIGQUERY_COLUMN_NAMES = [
        "Title",
        "Artist",
        "Album",
        "Datetime",
        "Title_c",
        "Artist_c",
        "Datetime_n",
    ]

    # Reorder `append`'s order of columns to match exactly that of bq's
    df = df[BIGQUERY_COLUMN_NAMES]

    # Convert col type to one that is compatible with bq
    df["Datetime_n"] = pd.to_datetime(df["Datetime_n"], format="%Y-%m-%d %H:%M:%S")

    bq_client.load_table_from_dataframe(
        dataframe=df,
        destination=table_ref_str,
        job_config=bq.job.LoadJobConfig(write_disposition="WRITE_APPEND"),
    )
    logger.info(f"Successfully appended to {table_ref_str}")
