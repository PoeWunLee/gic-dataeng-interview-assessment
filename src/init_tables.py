from pathlib import Path
from utils.db_utils import init_db_connect, execute_sql_to_db
from utils.file_utils import extract_sql_from_file

def init_tables(init_db_configs:dict[str:str], root_sql_path:Path)->None:
    """Based on config dict, initialise tables required"""

    #TODO: Implement better logging
    for sql_file_path in init_db_configs.values():
        #obtain absolute path
        sql_full_path = root_sql_path / sql_file_path
        #open and parse sql commands
        sql = extract_sql_from_file(sql_full_path)

        #execute DDL command
        with init_db_connect() as cnxn:
            execute_sql_to_db(sql, cnxn, is_bulk_ingest=True)
    
    return