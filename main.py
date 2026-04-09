from pathlib import Path
import os
import logging
from dotenv import load_dotenv

#load configs
from config.file_configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT, STAGING_FILENAME_EXT
from config.db_configs import INIT_DB_SCRIPTS, FUND_TABLE_NAME
from config.analytics_configs import ANALYTICS_INPUT_OUTPUT_DICT

#load generic utils
from utils.file_utils import get_files, generate_dir, get_paths
from utils.log_utils import init_logger
from utils.config_utils import ConfigParser

#load scripts
from src.etl import run_pipeline
#load environment variables
load_dotenv()
CNXN_STR = os.getenv("CNXN_STR")

#initialise logging configs
init_logger()


def main()->None:
    """Main entrypoint function to run extract, stage, load, analyse steps"""
    #initialise paths
    root = Path(__file__).parent.absolute()
    paths=get_paths(root)

    #ensure .env file has CNXN_STR - sqlite3
    if not CNXN_STR:
        raise ValueError("Please insert valid DB connection string/sqlite3 .db in environment variables")
    
    #parse configs
    configs=ConfigParser(raw_filename_ext=RAW_FILENAME_EXT,
        staging_filename_ext=STAGING_FILENAME_EXT,
        parse_raw_details_config=PARSE_RAW_DETAILS_CONFIG,
        fund_table_name=FUND_TABLE_NAME,
        init_db_scripts=INIT_DB_SCRIPTS,
        analytics_input_output_dict=ANALYTICS_INPUT_OUTPUT_DICT,
        cnxn_str=CNXN_STR)

    try:
        run_pipeline(paths=paths, configs=configs)
    except Exception:
        logging.exception("Pipeline run failed.")
        raise

if __name__=="__main__":
    main()