from __future__ import annotations
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Generator
from pathlib import Path
from contextlib import contextmanager
import pandas as pd
import logging

logging.getLogger(__name__)

@contextmanager
def init_db_connect(cnxn_str:str)->Generator[Connection, None, None]:
    """Initialise database connection and cursor to local sqlite3 - ensure clean commits and rollback. 
    Creates db if not yet exists."""
    #initialise conn value
    conn=None
    try:
        conn = sqlite3.connect(cnxn_str)
        yield conn
    except Exception:
        if conn:
            conn.rollback()
        logging.exception("Connection failed to database.")
        raise 
    finally:
        if conn:
            conn.close()

#generic sql statement -> DB
def execute_sql_to_db(sql:str, conn:Connection, is_bulk_ingest=False)->tuple[list[tuple],list[str]]|None:
    """Cursor execution function to execute sql on sqllite3. Supports bulk ingestion with executescripts (i.e. multi-statements) into DB.""" 
    ctx = None
    try:
        ctx = conn.cursor()
        if is_bulk_ingest:
            ctx.executescript(sql)
            return
        #use normal execute utility if not ingestion, which returns results
        ctx.execute(sql)
        results = ctx.fetchall()
        cols=[description[0] for description in ctx.description]
        return results, cols
    finally:
        if ctx:
            ctx.close()

#cursor results from DB -> pandas DF
def df_from_sql_results(results:list[tuple]|None, cols:list[str]) -> pd.DataFrame:
    """Load sql results as dataframe"""
    results_as_df = pd.DataFrame(results, columns=cols)
    return results_as_df

#pandas insert into -> DB
def insert_df_to_db(df:pd.DataFrame, conn:Connection, destination_table:str)->None:
    """Direct utility of loading data from pandas dataframe to SQL table"""
    df.to_sql(destination_table,conn, if_exists="append", index=False)