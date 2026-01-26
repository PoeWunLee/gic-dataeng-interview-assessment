from pathlib import Path
import os
import logging
from dotenv import load_dotenv

#load configs
from config.file_configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT, STAGING_FILENAME_EXT
from config.db_configs import DB_HOST, INIT_DB_SCRIPTS, FUND_TABLE_NAME
from config.analytics_configs import ANALYTICS_INPUT_OUTPUT_DICT

#load generic utils
from utils.file_utils import get_files
from utils.log_utils import init_logger

#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data

#iload environment variables
load_dotenv()
CNXN_STR = os.getenv("CNXN_STR")

#initialise logging configs
init_logger()

#parsing paths
def get_paths()->dict[str:Path]:
    root = Path(__file__).parent.absolute()
    return {
        "root":root,
        "raw":root / "data" / "raw",
        "staging":root / "data" / "staging",
        "sql":root / "sql",
        "analytics":root / "data" / "analytics",
        "config":root / "config"
    }

#wrapper for each step
def run_init_tables(path:dict[str:Path]):
    """Init DB and tables"""
    logging.info("STARTED: [INITALISE]")
    init_tables(CNXN_STR,init_db_configs=INIT_DB_SCRIPTS, root_sql_path=path["sql"])
    logging.info("COMPLETED: [INITALISE]\n")

def extract(path:dict[str:Path]):
    """Extract step - from raw -> staging directory"""
    logging.info("STARTED: [EXTRACT]")
    raw_files = get_files(dir=path["raw"], ext=RAW_FILENAME_EXT)
    extract_raw_to_stage(raw_files, path["staging"], PARSE_RAW_DETAILS_CONFIG)
    logging.info("COMPLETED: [EXTRACT]\n")

def load(path:dict[str:Path]):
    """Load step - from staging directory -> sqlite"""
    logging.info("STARTED: [LOAD]")
    staged_files = get_files(dir=path["staging"], ext=STAGING_FILENAME_EXT)
    load_funds(CNXN_STR,staged_files, FUND_TABLE_NAME)
    logging.info("COMPLETED: [LOAD]\n")

def analyse(path:dict[str:Path]):
    """Analysis step - sqlite -> csv exports in analytics directory"""
    logging.info("STARTED: [ANALYTICS]")
    analyse_data(CNXN_STR,ANALYTICS_INPUT_OUTPUT_DICT, path["sql"], path["analytics"])
    logging.info("COMPLETED: [ANALYTICS]\n")

def main():
    """Main entrypoint function to run extract, stage, load, analyse steps"""
    path=get_paths()
    try:
        if not os.path.isfile(DB_HOST):
            run_init_tables(path)
        extract(path)
        load(path)
        analyse(path)
    except Exception:
        logging.exception("Pipeline run failed.")
        raise

if __name__=="__main__":
    main()