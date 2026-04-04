from dataclasses import dataclass
from pathlib import Path
#load configs
from configs import CNXN_STR,ANALYTICS_INPUT_OUTPUT_DICT,INIT_DB_SCRIPTS, FUND_TABLE_NAME,PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT, STAGING_FILENAME_EXT

@dataclass
class InitialiseConfigs:
    cnxn_str:str
    init_db_scripts:dict[str,str]

@dataclass
class ExtractConfigs:
    raw_filename_ext:str
    parse_raw_details_config:dict[str,str]

@dataclass
class LoadConfigs:
    cnxn_str:str
    staging_filename_ext:str
    fund_table_name:str

@dataclass
class AnalyseConfigs:
    cnxn_str:str
    analytics_input_output_dict:dict[str,dict[str,str]]

class Configs:
    def __init__( 
        self,
        init_confiigs:InitialiseConfigs, 
        extract_configs:ExtractConfigs, 
        load_configs:LoadConfigs,
        analyse_configs:AnalyseConfigs        
    ):
        self.init_configs=init_confiigs
        self.extract_configs=extract_configs
        self.load_configs=load_configs
        self.analyse_configs=analyse_configs


def parse_configs():
    """Utility function to load and parse all config vars required based on current configs file"""
    init_configs = InitialiseConfigs(CNXN_STR, INIT_DB_SCRIPTS)
    extract_configs = ExtractConfigs(RAW_FILENAME_EXT, PARSE_RAW_DETAILS_CONFIG)
    load_configs = LoadConfigs(CNXN_STR, STAGING_FILENAME_EXT, FUND_TABLE_NAME)
    analyse_configs = AnalyseConfigs(CNXN_STR,ANALYTICS_INPUT_OUTPUT_DICT)

    configs = Configs(init_configs, extract_configs, load_configs, analyse_configs)

    return configs