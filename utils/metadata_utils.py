
from pathlib import Path
import pandas as pd
import re
import logging

#logging
logging.getLogger(__name__)

def get_details_from_filename(filename:str, regex_exp:str, details_tag:str)->str|None:
    """Determine metadata from csv filename based on regex expression mapping"""
    matched_details= re.findall(regex_exp, filename, re.IGNORECASE)
    if len(matched_details) < 1:
        logging.exception(f"Could not map {filename} to any {details_tag}")
        return
    return matched_details[0]

def parse_raw_details(filename:Path, raw_config:dict[str:str])->dict[str:str]:
    """"Retrieve each file's fund name and date from regex"""
    filename_str = str(filename) #conversion to str for regexp input
    parsed_results = {
        metadata_field:get_details_from_filename(filename_str, regex_expression, metadata_field) \
            for metadata_field,regex_expression in raw_config.items()
    }
    return parsed_results

def parse_datetime_format(date_time_raw:str)->pd.Series|None:
    """Further parsing datetime utility"""
    date_time_cleaned = date_time_raw.replace("_", "-")
    try:
        date_time_converted = pd.to_datetime(date_time_cleaned, format="mixed") #account for variety of datetime formats
        return date_time_converted
    except:
        logging.exception(f"Unable to parse {date_time_raw} to a valid datetime format extracted from filename.")
        raise

def parse_staging_pathname(dest_root_path:Path,fund_name:str, date_str:str)->tuple[Path:Path]:
    """Parses and returns required staging files dir and filenames based on metadata"""
    stage_file_dir = dest_root_path / date_str
    staged_file_name = stage_file_dir / f"{fund_name}.csv"
    return stage_file_dir, staged_file_name

def enrich_raw_df_with_details(df:pd.DataFrame, fund_name:str, date_time:str)->pd.DataFrame:
    """Enrich fund name and details to the dataframe"""
    enriched_df = df.copy()
    enriched_df['FUND'] = fund_name.capitalize()
    enriched_df['DATETIME'] = parse_datetime_format(date_time) 
    return enriched_df