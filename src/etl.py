
import logging
from pathlib import Path
from src.init_tables import init_tables
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.analytics import analyse_data

#load utils
from utils.file_utils import get_files
from utils.config_utils import ConfigsParser, InitialiseConfigs, ExtractConfigs, LoadConfigs, AnalyticsConfigs

class PipelineStatus:
    extracted_files:int=0
    loaded_files:int=0
    analysed_files:int=0

class PipelineRun:
    def __init__(self, configs:ConfigsParser,is_initialise:bool, is_extract:bool, is_load:bool, is_analyse:bool):
        self.configs = configs
        self.is_initialise = is_initialise
        self.is_extract = is_extract
        self.is_load = is_load
        self.is_analyse = is_analyse

    def initialise(self,config:InitialiseConfigs,path:dict[str,Path],cnxn_str:str):
        """Initialise DB and required tables (bond and equity references, bond and equity price, fund position)"""
        logging.info("STARTED: [INITALISE]")
        init_tables(cnxn_str,init_db_configs=config.init_db_scripts, root_sql_path=path["sql"])
        logging.info("COMPLETED: [INITALISE]\n")


    def extract(self,config:ExtractConfigs,path:dict[str,Path])->int|None:
        """Extract step - from raw -> staging directory"""
        logging.info("STARTED: [EXTRACT]")
        raw_files = get_files(dir=path["raw"], ext=config.raw_filename_ext)
        extracted_file_count= extract_raw_to_stage(raw_files, path["staging"], config.parse_raw_details_config)
        logging.info("COMPLETED: [EXTRACT]\n")

        return extracted_file_count

    def load(self,config:LoadConfigs,path:dict[str,Path], cnxn_str:str)->int|None:
        """Load step - from staging directory -> sqlite"""
        logging.info("STARTED: [LOAD]")
        staged_files = get_files(dir=path["staging"], ext=config.staging_filename_ext)
        loaded_file_count = load_funds(cnxn_str,staged_files, config.fund_table_name)
        logging.info("COMPLETED: [LOAD]\n")

        return loaded_file_count

    def analyse(self,config:AnalyticsConfigs,path:dict[str,Path],cnxn_str:str):
        """Analysis step - sqlite -> csv exports in analytics directory"""
        logging.info("STARTED: [ANALYTICS]")
        analysis_file_count = analyse_data(cnxn_str,config.analytics_input_output_dict, path["sql"], path["analytics"])
        logging.info("COMPLETED: [ANALYTICS]\n")

        return analysis_file_count

    def run(self,path:dict[str,Path],cnxn_str:str):
        #pipeline status
        status = PipelineStatus()
        
        if self.is_initialise:
            init_config = self.configs.init_configs
            self.initialise(init_config,path, cnxn_str)

        if self.is_extract:
            extract_config = self.configs.extract_configs
            status.extracted_files = self.extract(extract_config,path)

        if self.is_load:
            load_config = self.configs.load_configs
            status.loaded_files=self.load(load_config,path,cnxn_str)

        if self.is_analyse:
            analytics_config = self.configs.analytics_configs
            status.analysed_files=self.analyse(analytics_config,path, cnxn_str)
        
        logging.info("Staged:{} files | Loaded:{} rows | Analysed:{} analyses".format(status.extracted_files, status.loaded_files, status.analysed_files))
        
        return status