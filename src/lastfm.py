from collections import namedtuple
from datetime import datetime, timedelta
import logging
from typing import Dict, List

import pandas as pd
import requests

# PAGE_RETRIEVE_COUNT = os.environ["PAGE_RETRIEVE_COUNT"]
# LASTFM_USERNAME = os.environ["LASTFM_USERNAME"]
# LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]

logger = logging.getLogger("main.lastfm")


def get_df_lastfm(
    lastfm_username: str, last_apikey: str, page_num: int
) -> pd.DataFrame:
    """Use last.fm API, get n pages of scrobblesm then convert to pandas df.

    Last.fm scrobbles datetime has to be shifted 8 hours forward to get SGT.
    """
    pages: List[int] = list(range(1, page_num + 1))
    page_ls = []
    for p in pages:
        payload: Dict[str, str] = {
            "limit": str(200),
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
                f"Status Code of {r.status_code} from {r.url}. Aborting."
            )
    logger.info("Last.fm: Retrieval of JSON object from last.fm " + "API successful")

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
