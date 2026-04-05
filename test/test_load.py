import pytest
import sys
from pathlib import Path
import pandas as pd
import sqlite3

CURRENT_FILE_DIR=Path(__file__).parent.parent.absolute()
sys.path.append(CURRENT_FILE_DIR)
from utils.db_utils import init_db_connect
from src.load_data import load_funds

@pytest.fixture
def make_connection(tmp_path:Path):
    """Fixture for temporary testing DB"""
    conn=sqlite3.connect(tmp_path/"test.db")
    ctx = conn.cursor()
    #create table from sql
    create_statement = f"""CREATE TABLE IF NOT EXISTS "fund_position" (
    "FINANCIAL TYPE"    TEXT,
    "SYMBOL"    TEXT,
    "SECURITY NAME" TEXT,
    "SEDOL" TEXT,
    "ISIN" TEXT,
    "PRICE" REAL,
    "QUANTITY" REAL,
    "REALISED P/L" REAL,
    "MARKET VALUE" REAL,
    "FUND" TEXT,
    "DATETIME" TEXT
    );"""
    ctx.execute(create_statement)
    conn.commit()
    conn.close()

@pytest.fixture
def make_staging(tmp_path:Path, input_date_partition:str,input_fund_csv:str):
    """Fixture to create tmp directory and files for staging"""

    #provide and make directory for staging
    tmp_dir = tmp_path/"staging"/input_date_partition
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file=tmp_dir/input_fund_csv
    fund_name=input_fund_csv.split(".")[0]

    #write dummy data
    with open(tmp_file, 'w') as f:
        f.write(f"""FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE,FUND,DATETIME\n
    Equities,AVGO,Broadcom Inc.,,460.45,138610.07658144084,589429.6018720224,63823009.76192443,{fund_name},{input_date_partition}""")
    
    return tmp_file

@pytest.mark.parametrize(
        "input_date_partition, input_fund_csv",
        [
            ("2022-01-31","APPLEBEAD.csv"),
            ("2023-08-31","BELAWARE.csv"),
            ("2022-11-30","CATALYSM.csv"),
            ("2023-02-28","GOHEN.csv"),
            ("2025-06-30","LEEDER.csv"),
            ("2024-05-31","MAGNUM.csv"),
            ("2024-04-30","TRUSTMIND.csv"),
            ("2024-07-31","VIRTOUS.csv"),
            ("2021-10-30","WALLINGTON.csv"),
            ("2019-03-31","WHITESTONE.csv")
        ]
)
def test_load_funds(input_date_partition, input_fund_csv, make_staging,make_connection, tmp_path):
    """Unit testing for main load logic"""
    #arrange - connection and staging files and directories
    csv_path = make_staging
    make_connection

    #act - load, and retrieve DB loaded results from select query
    load_funds(tmp_path/"test.db",[csv_path], "fund_position")
    with init_db_connect(tmp_path/"test.db") as cnxn:
        ctx = cnxn.cursor()
        ctx.execute("SELECT * FROM fund_position;")
        result=ctx.fetchall()
        cols=[description[0] for description in ctx.description]

    #assert - test columns and records (both enriched fund & datetine metadata) and as-is data from raw align 
    df_from_query = pd.DataFrame(result, columns=cols)
    df_from_csv = pd.read_csv(csv_path)

    assert list(df_from_query.columns)==list(df_from_query.columns)
    assert df_from_query["FUND"].iloc[0] == input_fund_csv.split(".")[0]
    assert df_from_query["DATETIME"].iloc[0] == input_date_partition
    assert df_from_query["SYMBOL"].iloc[0] == df_from_csv["SYMBOL"].iloc[0]
    assert df_from_query["MARKET VALUE"].iloc[0] == df_from_csv["MARKET VALUE"].iloc[0]
