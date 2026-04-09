#wrapper for each step
#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data

from utils.config_utils import ConfigParser
from utils.file_utils import get_files
import logging
import os
from pathlib import Path

def initialise(paths:Path,configs:ConfigParser,funds=None, dates=None):
    """Initialise DB and required tables (bond and equity references, bond and equity price, fund position)"""
    logging.info("STARTED: [INITALISE]")
    init_tables(configs.cnxn_str,init_db_configs=configs.init_db_scripts, root_sql_path=paths["sql"])
    logging.info("COMPLETED: [INITALISE]\n")

def extract(paths:Path,configs:ConfigParser,funds=None, dates=None):
    """Extract step - from raw -> staging directory"""
    logging.info("STARTED: [EXTRACT]")
    raw_files = get_files(dir=paths["raw"], ext=configs.raw_filename_ext)
    extracted_files = extract_raw_to_stage(raw_files, paths["staging"], configs.parse_raw_details_config, funds, dates)
    logging.info("COMPLETED: [EXTRACT]\n")

    return extracted_files

def load(paths:Path,configs:ConfigParser,funds=None, dates=None):
    """Load step - from staging directory -> sqlite"""
    logging.info("STARTED: [LOAD]")
    staged_files = get_files(dir=paths["staging"], ext=configs.staging_filename_ext)
    loaded_files = load_funds(configs.cnxn_str,staged_files, configs.fund_table_name, funds,dates)
    logging.info("COMPLETED: [LOAD]\n")
    return loaded_files

def analyse(paths:Path,configs:ConfigParser,funds=None, dates=None):
    """Analysis step - sqlite -> csv exports in analytics directory"""
    logging.info("STARTED: [ANALYTICS]")
    analysis_completed = analyse_data(configs.cnxn_str,configs.analytics_input_output_dict, paths["sql"], paths["analytics"],funds,dates)
    logging.info("COMPLETED: [ANALYTICS]\n")
    return analysis_completed

def run_pipeline(paths:Path,configs:ConfigParser,funds=None, dates=None):
    if not os.path.isfile(paths["root"]/configs.cnxn_str):
        initialise(paths,configs,funds, dates)
    extracted_files = extract(paths,configs,funds, dates)
    loaded_files = load(paths,configs,funds, dates)
    analysis_completed = analyse(paths,configs,funds, dates)

    return extracted_files, loaded_files, analysis_completed