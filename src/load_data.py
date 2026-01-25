from pathlib import Path
import pandas as pd
from typing import Generator

from utils.file_utils import extract_csv_to_df
from utils.db_utils import insert_df_to_db, init_db_connect

def load_funds(files:Generator, destination_table:str)->None:
    """Load raw csv into funds table within the same date path"""

    # 1. load respective csvs into dfs. compile all staged into single csv
    stage_pd_lst = []
    for f in files:
        stage_pd_lst.append(extract_csv_to_df(f))
    dfs_staged = pd.concat(stage_pd_lst)

    #2. insert into table
    with init_db_connect() as cnxn:
        insert_df_to_db(dfs_staged, cnxn, destination_table)
    
    return