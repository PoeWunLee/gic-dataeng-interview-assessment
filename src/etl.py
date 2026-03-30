
import logging
from pathlib import Path
from init_tables import init_tables
from extract_data import extract_raw_to_stage
from load_data import load_funds
from analytics import analyse_data

#load configs
from config.file_configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT, STAGING_FILENAME_EXT
from config.db_configs import INIT_DB_SCRIPTS, FUND_TABLE_NAME
from config.analytics_configs import ANALYTICS_INPUT_OUTPUT_DICT

#load utils
from utils.file_utils import get_files

class PipelineStatus:
    extracted_files:int=0
    loaded_files:int=0
    analysed_files:int=0

class PipelineRun:
    def __init__(self, is_initialise:bool, is_extract:bool, is_load:bool, is_analyse:bool):
        self.is_initialise = is_initialise
        self.is_extract = is_extract
        self.is_load = is_load
        self.is_analyse =  is_analyse

    def initialise(self,path:dict[str,Path],cnxn_str:str):
        """Initialise DB and required tables (bond and equity references, bond and equity price, fund position)"""
        logging.info("STARTED: [INITALISE]")
        init_tables(cnxn_str,init_db_configs=INIT_DB_SCRIPTS, root_sql_path=path["sql"])
        logging.info("COMPLETED: [INITALISE]\n")

    def extract(self,path:dict[str,Path])->int|None:
        """Extract step - from raw -> staging directory"""
        logging.info("STARTED: [EXTRACT]")
        raw_files = get_files(dir=path["raw"], ext=RAW_FILENAME_EXT)
        extracted_file_count= extract_raw_to_stage(raw_files, path["staging"], PARSE_RAW_DETAILS_CONFIG)
        logging.info("COMPLETED: [EXTRACT]\n")

        return extracted_file_count

    def load(self,path:dict[str,Path], cnxn_str:str)->int|None:
        """Load step - from staging directory -> sqlite"""
        logging.info("STARTED: [LOAD]")
        staged_files = get_files(dir=path["staging"], ext=STAGING_FILENAME_EXT)
        loaded_file_count = load_funds(cnxn_str,staged_files, FUND_TABLE_NAME)
        logging.info("COMPLETED: [LOAD]\n")

        return loaded_file_count

    def analyse(self,path:dict[str,Path],cnxn_str:str):
        """Analysis step - sqlite -> csv exports in analytics directory"""
        logging.info("STARTED: [ANALYTICS]")
        analysis_file_count = analyse_data(cnxn_str,ANALYTICS_INPUT_OUTPUT_DICT, path["sql"], path["analytics"])
        logging.info("COMPLETED: [ANALYTICS]\n")

        return analysis_file_count

    def run(self,path:dict[str,Path],cnxn_str:str):
        #pipeline status
        status = PipelineStatus()
        
        if self.is_initialise:
            self.initialise(path, cnxn_str)

        if self.is_extract:
            status.extracted_files = self.extract(path)

        if self.is_load:
            status.loaded_files=self.load(path,cnxn_str)

        if self.is_analyse:
            status.analysed_files = self.analyse(path, cnxn_str)
        
        return status