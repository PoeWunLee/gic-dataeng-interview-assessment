from pathlib import Path
import pandas as pd
from typing import Generator
import logging

#dir imports
ROOT_DIR=Path(__file__).parent.parent.absolute()
from utils.file_utils import extract_csv_to_df, save_df_to_csv, generate_dir
from utils.metadata_utils import parse_raw_details,enrich_raw_df_with_details, parse_staging_pathname

#logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def extract_raw_to_stage(files:Generator, dest_root_path:Path, config:dict[str:str]) ->None:
    """Extract raw CSV with metadata enrichment, then save to file system based staging"""
    df_by_mth_dict = pd.DataFrame()

    for f in files:
        print(f)
        #1. extract csv to dataframe
        formatted_df = extract_csv_to_df(f)

        #2. obtain fund name and dates metadata from raw csv
        parsed_results = parse_raw_details(f, config)
        fund_name = parsed_results["fund_name"]
        date_time = parsed_results["date_time"]

        #3. enriching fund name and datetime metadata to the DataFrame
        enriched_df = enrich_raw_df_with_details(formatted_df, fund_name, date_time)

        #4. save enriched dataframe to staging file directories by month
        date_str = enriched_df['DATETIME'].unique().strftime('%Y-%m-%d')[0]
        stage_file_dir, staged_file_name = parse_staging_pathname(dest_root_path,fund_name, date_str)
        generate_dir(stage_file_dir)
        save_df_to_csv(enriched_df, staged_file_name)
    
        # if date_str in df_by_mth_dict.keys():
        #     df_by_mth_dict[date_str] = pd.concat(df_by_mth_dict[date_str], enriched_df)
        # else:
        #     df_by_mth_dict[date_str] = enriched_df
    
    return

