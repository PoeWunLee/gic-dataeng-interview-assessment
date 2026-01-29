from pathlib import Path
from utils.db_utils import init_db_connect, execute_sql_to_db
from utils.file_utils import extract_sql_from_file
import logging

logging.getLogger(__name__)

def init_tables(cnxn_str:str,init_db_configs:dict[str,str], root_sql_path:Path)->None:
    """Running sql DDL to initialise tables required in database."""
    for sql_file_path in init_db_configs.values():
        #1. obtain absolute path
        sql_full_path = root_sql_path / sql_file_path

        try:            
            #2. read sql from file
            sql = extract_sql_from_file(sql_full_path)

            #3. execute DDL commands
            with init_db_connect(cnxn_str) as cnxn:
                execute_sql_to_db(sql, cnxn, is_bulk_ingest=True)
                
        except Exception:
            logging.exception("Failed to initialise database and tables.", exc_info=True)
            raise
    
    logging.info("Initialised all database and tables.")

    return