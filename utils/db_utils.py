from __future__ import annotations
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Generator
from pathlib import Path
from contextlib import contextmanager
import pandas as pd
import logging
from config.db_configs import DB_HOST

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

@contextmanager
def init_db_connect(cnxn_str:str=DB_HOST)->Generator[Connection, None, None]:
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
        raise 
    finally:
        if conn:
            conn.close()

#generic sql atatement -> DB
def execute_sql_to_db(sql:str, conn:Connection, is_bulk_ingest=False)->tuple[list[tuple],list[str]]|None:
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
    except Exception:
        logger.exception(f"Query {sql} failed.")
        raise
    finally:
        if ctx:
            ctx.close()

#pandas insert into DB
def insert_df_to_db(df:pd.DataFrame, conn:Connection, destination_table:str)->None:
    """Direct utility of loading data from pandas dataframe to SQL table"""
    try:
        df.to_sql(destination_table,conn, if_exists="append", index=False)
    except Exception:
        logger.exception(f"Failed to insert dataframe into {destination_table}.")
        raise

#query from DB to pandas
def df_from_sql_results(results:list[tuple]|None, cols:list[str]) -> pd.DataFrame:
    """Load sql results as dataframe"""
    results_as_df = pd.DataFrame(results, columns=cols)
    return results_as_df


# def query_to_df(sql:str, conn:Connection)->pd.DataFrame|None:
#     ctx = None
#     try:
#         ctx = conn.cursor()
#         ctx.execute(sql)
#         results = ctx.fetchall()
#         return pd.DataFrame(results, columns= [description[0] for description in ctx.description])
#     except Exception:
#         logger.exception(f"Query {sql} failed.")
#         raise
#     finally:
#         if ctx:
#             ctx.close()
#csv -> pandas -> DB. DB -> pandas -> csv
# sql -> DB or sql -> pandas -> DB