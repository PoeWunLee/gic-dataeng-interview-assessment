import pandas as pd
from typing import Generator
import logging
from utils.file_utils import extract_csv_to_df
from utils.db_utils import insert_df_to_db, init_db_connect

logging.getLogger(__name__)

def load_funds(cnxn_str:str,files:Generator, destination_table:str)->None:
    """Load raw csv into funds table within the same date path"""
    try:
        # 1. load respective csvs into dfs. compile all staged into single df
        stage_pd_lst = []
        for f in files:
            stage_pd_lst.append(extract_csv_to_df(f))
        dfs_staged = pd.concat(stage_pd_lst)

        #2. insert compiled df into table
        with init_db_connect(cnxn_str) as cnxn:
            insert_df_to_db(dfs_staged, cnxn, destination_table)
        
        logging.info(f"Loaded {len(dfs_staged)} records into database table {destination_table}.")
    except Exception:
        logging.exception(f"Load to database table {destination_table} failed.", exc_info=True)
    
    return