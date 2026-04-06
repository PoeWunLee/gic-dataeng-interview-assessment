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

def insert_sql_statement_from_df(df:pd.DataFrame, conn:Connection, destination_table:str)-> None:
    sql_statements = []
    update_statements = ['"{}"={}."{}"'.format(col,destination_table,col) for col in df.columns if col not in ("FUND", "DATETIME", "SYMBOL")]
    column_statements = ",".join(['"{}"'.format(col) for col in df.columns])
    df_formatted = df.copy().fillna(0)
    for i, row in df_formatted.iterrows():
        sql_statement = f"{str(tuple(row.values))}"
        sql_statements.append(sql_statement)
    
    consol_sql_statement = f"""INSERT INTO {destination_table} ({column_statements}) VALUES {str(",".join(sql_statements))} ON CONFLICT(FUND, DATETIME, SYMBOL) DO UPDATE SET {" , ".join(update_statements)};"""
    logging.info(consol_sql_statement)
    with conn as cnxn:
        execute_sql_to_db(consol_sql_statement,cnxn,is_bulk_ingest=True)
    return

def insert_df_to_db(df:pd.DataFrame, conn:Connection, destination_table:str)->None:
    """Insert data from pandas dataframe to database table"""
    df.to_sql(destination_table,conn, if_exists="append", index=False)