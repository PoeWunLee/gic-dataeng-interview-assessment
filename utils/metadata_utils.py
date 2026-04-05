
from pathlib import Path
import pandas as pd
import re
import logging

def get_details_from_filename(filename:str, regex_exp:str, details_tag:str)->str|None:
    """Determine metadata from csv filename based on regex expression mapping"""
    matched_details= re.findall(regex_exp, filename, re.IGNORECASE)
    if len(matched_details) < 1:
        logging.exception(f"Could not map {filename} to any {details_tag}")
        return
    if len(matched_details) > 1:
        logging.exception(f"{filename} contains more than one fund name: {matched_details}")
    return matched_details[0].upper()

def parse_raw_details(filename:Path, raw_config:dict[str,str])->dict[str,str]:
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
        date_time_converted = pd.to_datetime(date_time_cleaned, format="mixed") #account for variety of datetime formats4
        date_time_str = date_time_converted.strftime('%Y-%m-%d')
        return date_time_str
    except:
        logging.exception(f"Unable to parse {date_time_raw} to a valid datetime format extracted from filename.")
        raise

def parse_staging_pathname(dest_root_path:Path,fund_name:str, date_str:str)->tuple[Path,Path]:
    """Parses and returns required staging files dir and filenames based on metadata"""
    stage_file_dir = dest_root_path / date_str
    staged_file_name = stage_file_dir / f"{fund_name}.csv"
    return stage_file_dir, staged_file_name

def enrich_raw_df_with_details(df:pd.DataFrame, fund_name:str, date_time:str)->pd.DataFrame:
    """Enrich fund name and details to the dataframe"""
    enriched_df = df.copy()
    enriched_df['FUND'] = fund_name
    enriched_df['DATETIME'] = date_time
    return enriched_df

def filter_dates_to_load(target_date:str|list[str], staging_path:Path)->list[Path]|None:
    """Utility to filter dates to load into DB"""
    
    if isinstance(target_date, str):
        target_date_formatted = parse_datetime_format(target_date) #clean possible datetime formats
        staging_date_path = staging_path/target_date_formatted
        if not staging_date_path.is_dir():
            logging.exception("Staging directory for given date {} does not exist. Extract specified date first.".format(staging_date_path))
            return []
        search_dates = [staging_date_path]
    elif isinstance(target_date, list):
        target_date_dirs = []
        search_dates = []
        for td in target_date:
            staging_date_path = staging_path/parse_datetime_format(td)
            target_date_dirs += [staging_date_path]
            if staging_date_path.is_dir():
                search_dates += [staging_date_path]

        ineligible_dates = set(target_date_dirs) - set(search_dates)
        if len(search_dates)==0:
            logging.exception("All dates specified are ineligible {} and not staged. Skipping load step...".format(ineligible_dates))
            return []
        if len(ineligible_dates) > 0:
            logging.info("Skipping ineligible dates {}. Stage raw files from dates first.".format(ineligible_dates))
        
    return search_dates

def filter_funds_to_load(target_fund:str|list[str], eligible_fundnames:str,file_ext:str)->list[str]|None:
    """Utility to filter fund names to load into DB"""

    if isinstance(target_fund,str):
        if target_fund.lower() not in eligible_fundnames:
            logging.exception("{} not in eligible fundname. Register in config first.".format(search_fund))
            return []
        search_fund = [file_ext.replace("*",target_fund.upper())]
    elif isinstance(target_fund,list):
        target_fund_formatted = [file_ext.replace("*",tf.upper()) for tf in target_fund]
        search_fund = [file_ext.replace("*",tf.upper()) for tf in target_fund if tf.lower() in eligible_fundnames]
        ineligible_funds = set(target_fund_formatted) - set(search_fund)
        if len(search_fund)==0:
            logging.exception("All funds specified are ineligible {}. Skipping load step...".format(ineligible_funds))
            return []
        if len(ineligible_funds)>0:
            logging.info("Skipping ineligible funds {}. Register in config first.".format(ineligible_funds))

    return search_fund
