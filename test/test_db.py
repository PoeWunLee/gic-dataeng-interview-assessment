import pytest
import sys
from pathlib import Path
import pandas as pd

CURRENT_FILE_DIR=Path(__file__).parent.parent.absolute()
sys.path.append(CURRENT_FILE_DIR)
from utils.db_utils import insert_df_to_db, init_db_connect, select_query_to_df
from config.db_configs import DB_HOST


def arrange_db_table_cleanup(destination_table:str)->None:
    #arrange ingestion
    with init_db_connect() as cnxn:
        #drop table first before testing
        ctx = cnxn.cursor()
        ctx.execute(f"DROP TABLE IF EXISTS {destination_table};").fetchall()
        ctx.close()


@pytest.mark.parametrize(
    "input_df, input_destination_table, output",
    [
        (
            pd.DataFrame([["1", "testing"], ["2", "another_test"]], columns=["index_col", "some_text"]), 
            "testing_table", 
            [("1", "testing"), ("2", "another_test")]
        )
    ]

)
def test_insert_df_to_db(input_df, input_destination_table, output):

    #arrange drop table before ingestion
    arrange_db_table_cleanup(input_destination_table)
    
    with init_db_connect() as cnxn:
        ctx = cnxn.cursor()
        #insert data
        insert_df_to_db(input_df, cnxn,input_destination_table)
        #post ingestion - read data
        query_results = ctx.execute(f"SELECT * FROM {input_destination_table};").fetchall()
        ctx.close()

    assert query_results==output

@pytest.mark.parametrize(
    "input_df, input_table, input_sql,output",
    [
        (
            pd.DataFrame([["1", "testing"], ["2", "another_test"]], columns=["index_col", "some_text"]), 
            "testing_table", 
            "SELECT * FROM testing_table;",
            pd.DataFrame([["1", "testing"], ["2", "another_test"]], columns=["index_col", "some_text"])
        )
    ]

)
def test_select_query_to_df(input_df, input_table, input_sql,output):
    #arrange drop table before ingestion
    arrange_db_table_cleanup(input_table)
    
    #start ingestion
    with init_db_connect() as cnxn:
        #insert data
        insert_df_to_db(input_df, cnxn,input_table)
        #post ingestion - read data
        df_results = select_query_to_df(input_sql,cnxn, input_table)
    
    assert df_results.equals(output)