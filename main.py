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
from utils.configs_utils import parse_configs

#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data
from src.etl import PipelineRun, PipelineStatus

def main()->None:
    """Main entrypoint function to run extract, stage, load, analyse steps"""
    
    #load environment variables
    load_dotenv()
    root = Path(__file__).parent.absolute()

    #initialise logging configs
    init_logger()

    #initialise paths
    path=get_paths(root)
    configs=parse_configs()
    cnxn_str = configs.init_configs.cnxn_str #get cnxn string for checking

    #ensure .env file has CNXN_STR - sqlite3
    if not cnxn_str:
        raise ValueError("Please insert valid DB connection string/sqlite3 .db in environment variables")

    is_init=False
    if ".db" in cnxn_str and not os.path.isfile(cnxn_str):
        is_init=True #initialise .db if sqlite3 matching CNXN_STR name not found in root directory
    
    try:
        pipeline = PipelineRun(configs,path,is_init)
        status = pipeline.run(target_date=["2023-02-28", "2022-10-31"], target_fund=["applebead", "belaware", "magnum"])

    except Exception:
        logging.exception("Pipeline run failed.")
        raise

if __name__=="__main__":
    main()