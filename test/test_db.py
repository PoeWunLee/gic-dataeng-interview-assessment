import pytest
import sys
from pathlib import Path
import pandas as pd

CURRENT_FILE_DIR=Path(__file__).parent.parent.absolute()
sys.path.append(CURRENT_FILE_DIR)
from utils.db_utils import insert_df_to_db, init_db_connect,execute_sql_to_db, df_from_sql_results
from config.db_configs import DB_HOST


def arrange_db_table_cleanup(cnxn_str:str,destination_table:str)->None:
    #arrange ingestion
    with init_db_connect(cnxn_str) as cnxn:
        #drop table first before testing
        ctx = cnxn.cursor()
        ctx.execute(f"DROP TABLE IF EXISTS {destination_table};").fetchall()
        ctx.close()

def arrange_db_create_table(cnxn_str:str,destination_table:str, columns:dict[str:str])->None:
    #arrange ingestion
    with init_db_connect(cnxn_str) as cnxn:
        #drop table first before testing
        ctx = cnxn.cursor()
        cols = ",\n".join(["{} {}".format(col_name, dtype) for col_name, dtype in columns.items()])
        create_statement = f"CREATE TABLE IF NOT EXISTS {destination_table} ({cols});"
        print(create_statement)
        ctx.execute(f"CREATE TABLE IF NOT EXISTS {destination_table} ({cols});").fetchall()
        ctx.close()

def arange_db_ingest_table(cnxn_str:str, destination_table, values):

    sql = """INSERT INTO {} VALUES ()"""
    with init_db_connect(cnxn_str) as cnxn:
        ctx = cnxn.cursor()
        #insert data
        ctx.execute(sql, cnxn)

@pytest.mark.parametrize(
    "input_cnxn_str,input_df, input_destination_table, output",
    [
        (   
            "test.db",
            pd.DataFrame([["1", "testing"], ["2", "another_test"]], columns=["index_col", "some_text"]), 
            "testing_table", 
            [("1", "testing"), ("2", "another_test")]
        )
    ]

)
def test_insert_df_to_db(input_cnxn_str,input_df, input_destination_table, output):

    #arrange drop table before ingestion
    arrange_db_table_cleanup(input_cnxn_str,input_destination_table)
    
    with init_db_connect(input_cnxn_str) as cnxn:
        ctx = cnxn.cursor()
        #insert data
        insert_df_to_db(input_df, cnxn,input_destination_table)
        #post ingestion - read data
        query_results = ctx.execute(f"SELECT * FROM {input_destination_table};").fetchall()
        ctx.close()

    assert query_results==output

@pytest.mark.parametrize(
        ""

)
def test_df_from_sql_results():
    pass

# @pytest.mark.parametrize(
#     "input_cnxn_str,input_destination_table,input_cols,input_sql,output_res",
#     [
#         (
#             "test_db",
#             "testing_table",
#             {"index_col" : "INTEGER", "some_text":"TEXT"},
#             """INSERT INTO "testing_table" (index_col, some_text) VALUES (1,'testing'),(2,'another_test');""", 

#             [[(1, "testing"), (2,"another_test")], ["index_col", "some_text"]]
#         )

#     ]

# )
# def test_execute_sql_to_db(input_cnxn_str,input_destination_table,input_cols,input_sql,output_res):
    
#     #arrange drop table 
#     arrange_db_table_cleanup(input_cnxn_str, input_destination_table)
#     #arrange create table 
#     arrange_db_create_table(input_cnxn_str, input_destination_table,input_cols)
#     #start ingestion
#     arange_db_ingest_table(input_cnxn_str, input_sql)
       
#      results = execute_sql_to_db(f"SELECT * FROM {input_destination_table};", cnxn)

    
#     assert results == output_res