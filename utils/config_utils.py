from dataclasses import dataclass

@dataclass
class InitialiseConfigs:
    init_db_scripts:dict[str,str]

@dataclass
class ExtractConfigs:
    raw_filename_ext:str
    parse_raw_details_config:dict[str,str]

@dataclass
class LoadConfigs:
    fund_table_name:str
    staging_filename_ext:str

@dataclass
class AnalyticsConfigs:
    analytics_input_output_dict:dict[str,dict[str,str]]

class ConfigsParser:
    def __init__(self, 
                init_configs:InitialiseConfigs, 
                extract_configs:ExtractConfigs, 
                load_configs:LoadConfigs, 
                analytics_configs:AnalyticsConfigs):
        self.init_configs = init_configs
        self.extract_configs = extract_configs
        self.load_configs=load_configs
        self.analytics_configs=analytics_configs
