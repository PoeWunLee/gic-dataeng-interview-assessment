import pandas as pd
from typing import Generator
import logging
from pathlib import Path
from utils.file_utils import extract_csv_to_df
from utils.db_utils import insert_df_to_db, init_db_connect

logging.getLogger(__name__)

def load_funds(cnxn_str:str,files:Generator, destination_table:str,funds:list[str]|None, dates:list[str]|None)->list[Path]|None:
    """Load raw CSV into funds table within the same date path"""
    loaded_files = []
    row_count = 0
    for f in files:
        try:
            #1. load respective csvs into dfs. compile all staged into single df

            dfs_staged = extract_csv_to_df(f)
            if funds:
                dfs_staged = dfs_staged.loc[dfs_staged["FUND"].isin(funds)]
            if dates:
                dfs_staged = dfs_staged.loc[dfs_staged["DATETIME"].isin(dates)]
            
            #2. insert compiled df into table
            with init_db_connect(cnxn_str) as cnxn:
                insert_df_to_db(dfs_staged, cnxn, destination_table)
            
            loaded_files.append(f)
            row_count += len(dfs_staged)

        except Exception:
            logging.exception(f"Load to database table {destination_table} failed.", exc_info=True)
            raise

    logging.info(f"Loaded {len(loaded_files)} files into database table {destination_table}. {row_count} rows inserted.")
        
    return loaded_files