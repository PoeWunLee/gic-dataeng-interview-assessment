import pytest
import os
from utils.file_utils import extract_sql_from_file
from utils.db_utils import execute_sql_to_db, df_from_sql_results, init_db_connect
from pathlib import Path
import pandas as pd

# ROOT_DIR=Path(__name__).parent.absolute()

# def arrange_sql_file(sql:str):
#     sql_filepath = ROOT_DIR/"tmp_dir"/"test_sql.sql"
#     if not os.path.exists(sql_filepath):
#         with open(sql_filepath) as f:
#             f.write(sql)

# def arrange_db_table_cleanup(cnxn_str:str,destination_table:str)->None:
#     #arrange ingestion
#     with init_db_connect(cnxn_str) as cnxn:
#         #drop table first before testing
#         ctx = cnxn.cursor()
#         ctx.execute(f"DROP TABLE IF EXISTS {destination_table};").fetchall()
#         ctx.close()

# def arrange_db_create_table(cnxn_str:str,destination_table:str, columns:dict[str:str])->None:
#     #arrange ingestion
#     with init_db_connect(cnxn_str) as cnxn:
#         #drop table first before testing
#         ctx = cnxn.cursor()
#         cols = ",\n".join(["{} {}".format(col_name, dtype) for col_name, dtype in columns.items()])
#         create_statement = f"CREATE TABLE IF NOT EXISTS {destination_table} ({cols});"
#         print(create_statement)
#         ctx.execute(f"CREATE TABLE IF NOT EXISTS {destination_table} ({cols});").fetchall()
#         ctx.close()

# def arange_db_ingest_table(cnxn_str:str, destination_table, values):

#     sql = """INSERT INTO {} VALUES ()"""
#     with init_db_connect(cnxn_str) as cnxn:
#         ctx = cnxn.cursor()
#         #insert data
#         ctx.execute(sql, cnxn)

# def arrange_csv_in_tmp_dir():
#     os.rmdir("tmp_dir")

# def arrange_tmp_dir():
#     os.mkdir("tmp_dir")

# @pytest.mark.parametrize(
#     "input_cols,rows, input_schema",
#     [
#         (   
#             ["DATETIME","FUND","RATE_OF_RETURN","CURRENT_TOTAL_MV","PREVIOUS_TOTAL_MV","CURRENT_TOTAL_PL","PREVIOUS_TOTAL_PL"], 
#             [("2022-09-30","Virtous",437.71659424576137,67852821.4152155,71643141.12847915,78785.35376366752,-8479.309234084216)],
#             ["TEXT", "TEXT", "REAL", "REAL", "REAL", "REAL", "REAL"]
        
#         ),
#         (   
#             ["DATETIME","FUND","DIFF_FROM_REF"], 
#             [("2022-10-31","Leeder",-1605.1459999999995)],
#             ["TEXT", "TEXT", "REAL"]
        
#         ),
#         (
#             ["DATETIME","FUND","INSTRUMENT_TYPE","SECURITY_NAME","IDENTIFIER","IDENTIFIER_TYPE","PRICE_FUND","PRICE_REF","DIFF_PRICE_REF"],
#             [("2022-10-31","Gohen","Government Bond","NETHERLANDS GOVERNMENT 3.75 % 01/15/2042 144A","NL0009446418","ISIN",170.85,187.935,-17.085000000000008)],
#             ["TEXT", "TEXT", "TEXT", "TEXT" ,"TEXT", "TEXT", "REAL", "REAL", "REAL"]
#         )
#     ]
# )
# def test_execute_sql_to_db(input_cols,rows, input_schema):
#     input_cnxn, input_destination_table = "test.db","test_table"
#     input_cols_dict = dict(zip(input_cols, input_schema))

#     #arrange
#     arrange_db_table_cleanup(input_cnxn,input_destination_table)
#     arrange_db_create_table(input_cnxn,input_destination_table, input_cols_dict)
#     cols_joined = ",".join(input_cols)
#     insert_sql = ";".join([f"INSERT INTO {input_destination_table} ({cols_joined}) VALUES {rows_to_insert}" for rows_to_insert in rows])
#     select_sql = f"SELECT * FROM {input_destination_table};"
    
#     #act
#     #test insert with is_bulk_ingest, then test select query
#     with init_db_connect(input_cnxn) as cnxn:
#         ingest_output = execute_sql_to_db(insert_sql, cnxn, True)
#         select_output_rows, select_output_cols= execute_sql_to_db(select_sql, cnxn, False)
    
#     output_df = df_from_sql_results(select_output_rows, select_output_cols)
#     expected_output_df=pd.DataFrame(rows, columns=input_cols)

#     #cleanup
#     arrange_db_table_cleanup(input_cnxn,input_destination_table)

#     #asserts
#     assert ingest_output==None
#     assert rows==select_output_rows
#     assert input_cols==select_output_cols
#     assert output_df.equals(expected_output_df)
