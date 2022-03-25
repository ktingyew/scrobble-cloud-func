"""Test connectivity and schema."""
import os
from pathlib import Path

from my_scrobble.gcs import load_mapper_as_df_from_bucket
from my_scrobble.lastfm import get_df_lastfm


class TestLastfm:
    """Last.fm test class."""

    def test_lastfm_schema(self):
        """Test lastfm schema."""
        LASTFM_USERNAME = os.environ["LASTFM_USERNAME"]
        LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]

        df = get_df_lastfm(
            lastfm_username=LASTFM_USERNAME,
            last_apikey=LASTFM_API_KEY,
            num_scrobs=100,
        )

        assert set(df.columns) == {"Datetime", "Datetime_n", "Artist", "Title", "Album"}


class TestCloudStorage:
    """Test set involving Google Cloud Storage."""

    def test_mapper_schema_from_gcs(self, tmp_path):
        """Download mapper.csv from GCS, then check its schema."""
        BUCKET_NAME = os.environ["BUCKET_NAME"]

        mapper = load_mapper_as_df_from_bucket(
            bucket_name=BUCKET_NAME,
            blob_name="mapper.csv",
            save_to_path=Path(tmp_path/"mapper.csv")
        )
        print(mapper.columns)
        assert set(mapper.columns) == {'Title_s', 'Artist_s', 'Title_c', 'Artist_c'}


class TestBigQuery:
    """Test set involving BigQuery."""

    pass
