#%%

from datetime import datetime, timedelta
import logging
from collections import namedtuple
import os
from pathlib import Path

import pandas as pd
import requests

PAGE_RETRIEVE_COUNT = os.environ['PAGE_RETRIEVE_COUNT']
LASTFM_USERNAME = os.environ['LASTFM_USERNAME']
LASTFM_API_KEY = os.environ['LASTFM_API_KEY']

logger = logging.getLogger("main.lastfm")


def get_df():

    pages = list(range(1, int(PAGE_RETRIEVE_COUNT)+1))
    page_ls = []
    for p in pages: 
        payload = {
            'limit': 200,
            'method': 'user.getrecenttracks', 
            'page': p,
            'user': LASTFM_USERNAME,
            'api_key': LASTFM_API_KEY,
            'format': 'json'
        }
        r = requests.get(
            'https://ws.audioscrobbler.com/2.0/', 
            params=payload
        )
        page_ls.append(r)
        
        if r.status_code != 200:
            raise ConnectionError(
                f"Status Code of {r.status_code} from {r.url}. Aborting.")
    logger.info(
        f"Last.fm: Retrieval of JSON object from last.fm " 
        + "API successful"
    )

    Scrobble = namedtuple("Scrobble", "Title Artist Album Datetime")
    records = []
    for page in page_ls:
        pg = page.json()['recenttracks']['track']
        for i in pg:
            try:
                records.append(
                    Scrobble(
                        i['name'], 
                        i['artist']['#text'], 
                        i['album']['#text'], 
                        i['date']['#text']
                    )
                )
            except KeyError:
                records.append(
                    Scrobble(
                        i['name'], 
                        i['artist']['#text'],
                        i['album']['#text'], 
                        None
                    )
                )

    # Drop entries with missing dt
    df = pd.DataFrame(data=records) \
        .dropna(axis=0, subset=['Datetime']) \
        .reset_index(drop=True) 

    # Adjust datetime of scrobbles 8-hours ahead (to SGT)
    dt_formatter = lambda x : (
        datetime.strptime(x, "%d %b %Y, %H:%M") \
        + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"
    )
    df['Datetime_n'] = df['Datetime'].apply(dt_formatter)

    logger.debug(f"Latest scrobble retrieved: {df.iloc[0].to_dict()}")


    return df

# %%

# Get current datetime
# dt_now_str : str = datetime.now().strftime("%Y-%m-%d %H-%M-%S") # SQL Datetime format

# filename = f"{dt_now_str} scrobble.jsonl"
# savepath = Path("/") / filename

# with open(savepath, 'w', encoding='utf-8') as fh:
#     new.to_json(fh, force_ascii=False, orient='records', lines=True) 
#     logger.info(
#         f"Scrobble: Successfully saved (n={len(new)}): {savepath}")

# %%

