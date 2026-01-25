import pandas as pd
from pathlib import Path
from typing import Generator
from sqlite3 import Connection, Cursor

CURRENT_FILE_DIR = Path(__file__).parent.parent.absolute()
RAW_DATA_DIR = CURRENT_FILE_DIR / "data" / "raw"

def load_reference(ctx:Cursor, ref_sql_path:Path)->None:
    """Load reference table"""
    with open(ref_sql_path, 'r') as f:
        sql_query=f.read()
    ctx.executescript(sql_query)

def load_funds(table_name:str,conn:Connection,funds_df:pd.DataFrame)->None:
    """Load raw csv into funds table"""
    funds_df.to_sql(name=table_name,con=conn, if_exists="append", index=False)