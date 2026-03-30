
from pathlib import Path
from utils.db_utils import init_db_connect,execute_sql_to_db, df_from_sql_results
from utils.file_utils import save_df_to_csv, extract_sql_from_file

import logging
logging.getLogger(__name__)

def analyse_data(cnxn_str:str, config_dict:dict[str,dict[str]], sql_root_dir:Path, export_root_dir:Path)->int|None:
    """Generated analysis from SQL query and export to CSV"""
    processed_analyses=0 #keep track of analyses executed
    for analysis, in_out_map in config_dict.items():
        for sql_file, csv_export_file in in_out_map.items():
            try:
                # 1. getting file paths for sql queries and csv export
                sql_filepath = sql_root_dir / sql_file
                csv_export_filepath = export_root_dir / csv_export_file

                # 2. extract sql from .sql
                sql_statement = extract_sql_from_file(sql_filepath) 

                #3. execute sql
                with init_db_connect(cnxn_str) as cnxn:
                    results, cols = execute_sql_to_db(sql_statement, cnxn)

                #4. save to df
                results_df = df_from_sql_results(results, cols)

                #5. save to csv
                save_df_to_csv(results_df,csv_export_filepath)
                
            except Exception:
                logging.exception(f"Analysis {analysis} failed to complete.", exc_info=True)
                raise

        logging.info(f"{analysis} analysis completed. Exported results to {list(in_out_map.values())}.")
        processed_analyses +=1
    
    return processed_analyses