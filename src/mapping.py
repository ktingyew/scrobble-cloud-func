import logging

import pandas as pd

logger = logging.getLogger("main.mapping")

def get_combined_mapped_scrobbles(
    new: pd.DataFrame,
    old: pd.DataFrame,
    mapper: pd.DataFrame
) -> pd.DataFrame :
    """
    `new` should be filtered already; records that already exist in
    `old` are removed.
    """

    # Filter away records from `new` that alr exists in `old`
    most_rct_datetime_from_old: str = old.iloc[0]['Datetime_n'] 
    idx: int = new[new['Datetime_n'] == most_rct_datetime_from_old].index.tolist()[0]
    new = new.iloc[:idx].copy() # new is thus modified

    for i in range(len(new)):
        title, artist = new.iloc[i]['Title'], new.iloc[i]['Artist'] 
        # attempt to look for "correct answer" in `mapper` by generating 
        # filtered df
        ans_df = mapper[
            (mapper['Artist_s'] == artist) 
            & (mapper['Title_s'] == title)
        ] 
        if len(ans_df) == 1: # there is an answer
            new.at[i, 'Title_c'] = ans_df.values.tolist()[0][2]
            new.at[i, 'Artist_c'] = ans_df.values.tolist()[0][3]
        else: # we populate the field with easy to find tags
            new.at[i, 'Title_c'] = "XXxXX"
            new.at[i, 'Artist_c'] =  "XXxXX" 

    # Concatenate new on top of old
    out = pd.concat([new, old], ignore_index=True)
    logger.debug(f"Size of out dataframe is {len(out)}")

    return out