"""Module to read scrobbles to DataFrame using last.fm API."""
from collections import namedtuple
from datetime import datetime, timedelta
import logging
import math
from typing import Dict, List

import pandas as pd
import requests

logger = logging.getLogger("main.lastfm")


def _get_raw_lastfm(
    lastfm_username: str,
    last_apikey: str,
    num_scrobs: int,
) -> List[requests.models.Response]:
    """Use last.fm API, get x most recent scrobbles.

    Where x is num_scrobs rounded up to nearest hundred.
    """
    num_pages: int = int(math.ceil(num_scrobs / 100.0))

    pages: List[int] = list(range(1, num_pages + 1))
    page_ls = []
    for p in pages:
        payload: Dict[str, str] = {
            "limit": "100",
            "method": "user.getrecenttracks",
            "page": str(p),
            "user": lastfm_username,
            "api_key": last_apikey,
            "format": "json",
        }
        r = requests.get("https://ws.audioscrobbler.com/2.0/", params=payload)
        page_ls.append(r)

        if r.status_code != 200:
            raise ConnectionError(
                f"Status Code of {r.status_code} from {r.url} when retrieving page"
                + f" {p}. Aborting."
            )
    logger.info("Last.fm: Retrieval of JSON object from last.fm " + "API successful")

    return page_ls


def get_df_lastfm(
    lastfm_username: str, last_apikey: str, num_scrobs: int
) -> pd.DataFrame:
    """Read num_scrobs most recent scrobbles, parse them into a DataFrame.

    num_scrobs is rounded up to nearest hundred.

    Last.fm scrobbles datetime has to be shifted 8 hours forward to get SGT.
    """
    page_ls: List[requests.models.Response] = _get_raw_lastfm(
        lastfm_username=lastfm_username, last_apikey=last_apikey, num_scrobs=num_scrobs
    )

    Scrobble = namedtuple("Scrobble", "Title Artist Album Datetime")
    records = []
    for page in page_ls:
        pg = page.json()["recenttracks"]["track"]
        for i in pg:
            try:
                records.append(
                    Scrobble(
                        i["name"],
                        i["artist"]["#text"],
                        i["album"]["#text"],
                        i["date"]["#text"],
                    )
                )
            except KeyError:
                records.append(
                    Scrobble(i["name"], i["artist"]["#text"], i["album"]["#text"], None)
                )

    # Drop entries with missing dt
    df = (
        pd.DataFrame(data=records)
        .dropna(axis=0, subset=["Datetime"])
        .reset_index(drop=True)
    )

    # Adjust datetime of scrobbles 8-hours ahead (to SGT)
    def dt_formatter(dt: str) -> str:
        return (datetime.strptime(dt, "%d %b %Y, %H:%M") + timedelta(hours=8)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # dt_formatter = lambda x: (
    #     datetime.strptime(x, "%d %b %Y, %H:%M") + timedelta(hours=8)
    # ).strftime("%Y-%m-%d %H:%M:%S")
    df["Datetime_n"] = df["Datetime"].apply(dt_formatter)

    logger.debug(f"Latest scrobble retrieved from last.fm: {df.iloc[0].to_dict()}")

    return df
