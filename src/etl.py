import logging
from pathlib import Path
import os

#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data

from utils.file_utils import get_files, get_paths
from utils.configs_utils import Configs, InitialiseConfigs, ExtractConfigs, LoadConfigs, AnalyseConfigs
from utils.metadata_utils import parse_datetime_format, filter_dates_to_load, filter_funds_to_load
from dataclasses import dataclass

@dataclass
class PipelineStatus:
    extract_status:int=0
    loaded_status:int=0
    analyse_status:int=0

class RunConfigs:
    fund_name:str=""
    date:str=""

class PipelineRun:
    def __init__(self, configs:Configs, paths:dict[str,Path],is_init:bool=False):
        #configs
        self.configs=Configs
        self.init_configs=configs.init_configs
        self.extract_configs=configs.extract_configs
        self.load_configs=configs.load_configs
        self.analyse_configs = configs.analyse_configs
        self.paths = paths
        self.is_init = is_init
    
    #wrapper for each step
    def initialise(self):
        """Initialise DB and required tables (bond and equity references, bond and equity price, fund position)"""
        logging.info("STARTED: [INITALISE]")
        init_tables(
            self.init_configs.cnxn_str,
            init_db_configs=self.init_configs.init_db_scripts, 
            root_sql_path=self.paths.get("sql")
        )
        logging.info("COMPLETED: [INITALISE]\n")

    def extract(self):
        """Extract step - from raw -> staging directory"""
        logging.info("STARTED: [EXTRACT]")
        try:
            raw_files = get_files(dir=self.paths.get("raw"), ext=self.extract_configs.raw_filename_ext)
            extracted_count = extract_raw_to_stage(raw_files, 
                                                self.paths.get("staging"), 
                                                self.extract_configs.parse_raw_details_config
                                                )
        except Exception as e:
            logging.exception("Failed to extract. {}".format(e))
            return 0
        logging.info("COMPLETED: [EXTRACT]\n")

        return extracted_count

    def load(self, target_date:str|list[str]|None=None, target_fund:str|list[str]|None=None):
        """Load step - from staging directory -> sqlite. Assumption - input target_date comes in either list of strings, stings or None"""
        logging.info("STARTED: [LOAD]")

        #initialised variables
        loaded_count=0

        file_ext = self.load_configs.staging_filename_ext
        eligible_fundnames = self.extract_configs.parse_raw_details_config.get("fund_name") #eligible fundnames
        staging_path = self.paths.get("staging")

        #placeholder - default values if no date or fund filters specified
        search_dates = [self.paths.get("staging")] #placeholder variable. default if no date is chosen.
        search_fund = None #placeholder variable. default if no date is chosen.
        staged_files_to_load = []

        try:
            #date filter
            if target_date:
                search_dates = filter_dates_to_load(target_date=target_date, staging_path=staging_path)
                if len(search_dates)==0:
                    return loaded_count
                logging.info("Dates to be loaded in to DB:{}".format(search_dates))

            #fund filter
            if target_fund:
                search_fund = filter_funds_to_load(target_fund=target_fund, eligible_fundnames=eligible_fundnames, file_ext=file_ext)
                if len(search_fund)==0:
                    return loaded_count
                logging.info("Funds to be loaded in to DB:{}".format(search_fund))
            
            for sd in search_dates:
                staged_files_to_load += get_files(dir=sd, ext=file_ext, filter_files=search_fund)
            
            loaded_count += load_funds(self.load_configs.cnxn_str,
                                    staged_files_to_load, 
                                    self.load_configs.fund_table_name
                            )
        except Exception as e:
            logging.exception("Failed to load. {}".format(e))
            return loaded_count
        logging.info("COMPLETED: [LOAD]\n")

        return loaded_count

    def analyse(self):
        """Analysis step - sqlite -> csv exports in analytics directory"""
        logging.info("STARTED: [ANALYTICS]")
        try:
            analysis_count = analyse_data(self.analyse_configs.cnxn_str,
                                        self.analyse_configs.analytics_input_output_dict, 
                                        self.paths.get("sql"), 
                                        self.paths.get("analytics")
                                        )
        except Exception as e:
            logging.exception("Failed to analyse.{}".format(e))
            return 0
        
        logging.info("COMPLETED: [ANALYTICS]\n")

        return analysis_count

    def run(self, target_date:str|list[str]|None=None, target_fund:str|list[str]|None=None):
        #initialise pipeline status
        status=PipelineStatus()
        if self.is_init:
            self.initialise()

        extract_status = self.extract()
        loaded_status = self.load(target_date, target_fund)
        analyse_status = self.analyse()

        logging.info("Extracted:{} files Loaded:{} rows Analysis outputs:{} files".format(extract_status, loaded_status, analyse_status))
        status=PipelineStatus(extract_status,loaded_status,analyse_status)
        
        return status




