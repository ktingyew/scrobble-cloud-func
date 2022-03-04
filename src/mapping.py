import logging

import pandas as pd

logger = logging.getLogger("main.mapping")


def filter_new_scrobbles(
    new: pd.DataFrame,
    date_string: str
) -> pd.DataFrame :
    """ Filter DataFrame, keeping only records that are after this date_string
    """
    df = new.copy()

    idx: int = df[df['Datetime_n'] == date_string].index.tolist()[0]
    df = df.iloc[:idx]

    logger.info(f"Number of new scrobbles: {len(df)}")

    return df


def map_the_new(
    new: pd.DataFrame,
    mapper: pd.DataFrame
) -> pd.DataFrame :
    """ Take the new df (of last.fm scrobbles), then map them with mapper.
    """
    df = new.copy()

    # Process new with mapper
    for i in range(len(df)):
        title, artist = new.iloc[i]['Title'], df.iloc[i]['Artist'] 
        # attempt to look for "correct answer" in `mapper` by generating 
        # filtered df
        ans_df = mapper[
            (mapper['Artist_s'] == artist) 
            & (mapper['Title_s'] == title)
        ] 
        if len(ans_df) == 1: # there is an answer
            df.at[i, 'Title_c'] = ans_df.values.tolist()[0][2]
            df.at[i, 'Artist_c'] = ans_df.values.tolist()[0][3]
        else: # we populate the field with easy to find tags
            df.at[i, 'Title_c'] = "XXxXX"
            df.at[i, 'Artist_c'] =  "XXxXX" 
            logger.warning(f"Mapper failed to map raw Scrobble: \n{new.iloc[i]}")

    return df
