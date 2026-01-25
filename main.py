from pathlib import Path
import sys
import os

ROOT_DIR = Path(__file__).parent.absolute()
RAW_DIR=ROOT_DIR / "data" / "raw"
STAGING_DIR=ROOT_DIR / "data" / "staging"
CONFIG_DIR=ROOT_DIR / "config"
SQL_DIR=ROOT_DIR / "sql"
ANLY_EXPORT_DIR = ROOT_DIR / "data" / "analytics"

from config.file_configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT
from config.db_configs import DB_HOST, INIT_DB_SCRIPTS, FUND_TABLE_NAME
from config.analytics_configs import ANALYTICS_INPUT_OUTPUT_DICT
from utils.file_utils import get_files
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse

def main():
    #run initialise for sqlite3 db if does not exist
    if not os.path.isfile(DB_HOST):
        init_tables(init_db_configs=INIT_DB_SCRIPTS, root_sql_path=SQL_DIR)

    # Extract step - from raw -> staging
    raw_files = get_files(RAW_DIR, RAW_FILENAME_EXT)
    extract_raw_to_stage(raw_files, STAGING_DIR, PARSE_RAW_DETAILS_CONFIG)

    # Load step - from staging -> sqlite
    staged_files = get_files(STAGING_DIR, RAW_FILENAME_EXT)
    load_funds(staged_files, FUND_TABLE_NAME)
    
    # Analysis step - sqlite -> csv exports
    analyse(ANALYTICS_INPUT_OUTPUT_DICT, SQL_DIR, ANLY_EXPORT_DIR)

if __name__=="__main__":
    main()