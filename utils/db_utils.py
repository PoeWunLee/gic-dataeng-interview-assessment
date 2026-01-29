from __future__ import annotations
import sqlite3
from sqlite3 import Connection
from typing import Generator
from contextlib import contextmanager
import pandas as pd
import logging

logging.getLogger(__name__)

@contextmanager
def init_db_connect(cnxn_str:str)->Generator[Connection, None, None]:
    """Initialise database connection and cursor to local sqlite3. Creates db if not yet exists."""
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
    """Cursor execution function to execute sql on sqllite3. Supports bulk ingestion into database.""" 
    ctx = None
    try:
        ctx = conn.cursor()
        if is_bulk_ingest:
            ctx.executescript(sql)
            return
        ctx.execute(sql)  #use normal execute utility if not ingestion, which returns results
        results = ctx.fetchall()
        cols=[description[0] for description in ctx.description]
        return results, cols
    finally:
        if ctx:
            ctx.close()

def df_from_sql_results(results:list[tuple]|None, cols:list[str]) -> pd.DataFrame:
    """Load sql results from cursor as dataframe"""
    results_as_df = pd.DataFrame(results, columns=cols)
    return results_as_df

def insert_df_to_db(df:pd.DataFrame, conn:Connection, destination_table:str)->None:
    """Insert data from pandas dataframe to database table"""
    df.to_sql(destination_table,conn, if_exists="append", index=False)