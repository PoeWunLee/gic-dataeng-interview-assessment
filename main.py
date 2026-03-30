from pathlib import Path
import os
import logging
from dotenv import load_dotenv

#load generic utils
from utils.file_utils import get_paths
from utils.log_utils import init_logger

#load scripts
from src.etl import PipelineRun

def main()->None:
    """Main entrypoint function to run extract, stage, load, analyse steps"""

    #directory management
    ROOT=Path(__file__).parent.absolute()
    #initialise logging configs
    init_logger()
    #initialise paths
    path=get_paths(ROOT)

    #get env vars
    load_dotenv(ROOT/".env")
    CNXN_STR = os.getenv("CNXN_STR")

    #ensure .env file has CNXN_STR - sqlite3
    if not CNXN_STR:
        raise ValueError("Please insert valid DB connection string/sqlite3 .db in environment variables")
    
    if ".db" in CNXN_STR and not os.path.isfile(CNXN_STR):
        is_initialise=True #auto initialise .db if sqlite3 , and if matching CNXN_STR name not found in root directory
    
    is_extract, is_load, is_analyse= True, True, True

    try:
        #initialise pipeline run
        pipeline = PipelineRun(is_initialise, is_extract, is_load, is_analyse)
        status = pipeline.run(path=path, cnxn_str=CNXN_STR)

    except Exception:
        logging.exception("Pipeline run failed.")
        raise

if __name__=="__main__":
    main()