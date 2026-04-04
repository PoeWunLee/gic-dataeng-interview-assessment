from pathlib import Path
import os
import logging
from dotenv import load_dotenv

#load generic utils
from utils.file_utils import get_paths
from utils.log_utils import init_logger
from utils.config_utils import InitialiseConfigs, ExtractConfigs, LoadConfigs, AnalyticsConfigs, ConfigsParser
from utils.cli_utils import get_cli_arguments

#load configs
from config.configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT, STAGING_FILENAME_EXT, INIT_DB_SCRIPTS, FUND_TABLE_NAME, ANALYTICS_INPUT_OUTPUT_DICT

#load scripts
from src.etl import PipelineRun

def main()->None:
    """Main entrypoint function to run extract, stage, load, analyse steps"""
    
    #initialising - logger, root path references, connection strings
    init_logger()
    
    ROOT=Path(__file__).parent.absolute() 
    path=get_paths(ROOT)
    load_dotenv(ROOT/".env")
    CNXN_STR = os.getenv("CNXN_STR")

    #ensure .env file has CNXN_STR - sqlite3
    if not CNXN_STR:
        raise ValueError("Please insert valid DB connection string/sqlite3 .db in environment variables")

    #flags for extract, load, analyse
    is_extract, is_load, is_analyse= get_cli_arguments()
    logging.info("{} {} {}".format(is_extract, is_load, is_analyse))

    #initialise flag set to true if sqlite and if env var does not have cnxn str
    is_initialise = ".db" in CNXN_STR and not os.path.isfile(CNXN_STR)

    #parse configs
    init_configs = InitialiseConfigs(init_db_scripts=INIT_DB_SCRIPTS)
    extract_configs = ExtractConfigs(raw_filename_ext=RAW_FILENAME_EXT,parse_raw_details_config=PARSE_RAW_DETAILS_CONFIG)
    load_configs= LoadConfigs(fund_table_name=FUND_TABLE_NAME, staging_filename_ext=STAGING_FILENAME_EXT)
    analytics_configs = AnalyticsConfigs(analytics_input_output_dict=ANALYTICS_INPUT_OUTPUT_DICT)
    configs = ConfigsParser(init_configs, extract_configs,load_configs,analytics_configs)

    try:
        #initialise pipeline run
        pipeline = PipelineRun(configs,is_initialise, is_extract, is_load, is_analyse)
        status = pipeline.run(path=path, cnxn_str=CNXN_STR)
    except Exception:
        logging.exception("Pipeline run failed.")
        raise

if __name__=="__main__":
    main()