from dataclasses import dataclass

@dataclass
class ConfigParser:
    # Scaling & conformity considerations - consider yml/class based approach for recognition of each fund by its own format
    raw_filename_ext:str
    staging_filename_ext:str 
    parse_raw_details_config:dict[str,str]
    fund_table_name:str
    init_db_scripts:dict[str,str]
    analytics_input_output_dict:dict[dict[str,StopAsyncIteration]]
    cnxn_str:str