from pathlib import Path
from typing import Generator
import logging
import pandas as pd
from utils.file_utils import extract_csv_to_df, save_df_to_csv, generate_dir
from utils.metadata_utils import parse_raw_details,enrich_raw_df_with_details, parse_staging_pathname, parse_datetime_format

def extract_raw_to_stage(files:Generator, dest_root_path:Path, raw_details_config:dict[str,str], funds:list[str]|None, dates:list[str]|None)->list[Path]|None:
    """Extract raw CSV with metadata enrichment, then save to staging directory"""
    files_processed=[] #keep track of files processed
    for f in files:
        try:
            #1. extract csv to dataframe
            formatted_df = extract_csv_to_df(f)

            #2. obtain fund name and dates metadata from raw csv
            parsed_results = parse_raw_details(f, raw_details_config)
            fund_name, date_time = parsed_results["fund_name"], parse_datetime_format(parsed_results["date_time"])
            
            #go to next file if files or funds not found in dates
            if funds and fund_name not in funds:
                continue
            if dates and date_time not in dates:
                continue

            #3. enriching fund name and datetime metadata to the DataFrame
            enriched_df = enrich_raw_df_with_details(formatted_df, fund_name, date_time)

            #4. save enriched dataframe to staging file directories by month
            stage_file_dir, staged_file_name = parse_staging_pathname(dest_root_path,fund_name, date_time)

            #5. Export and stage file
            generate_dir(stage_file_dir) #generate date directory if does not exist
            save_df_to_csv(enriched_df, staged_file_name)

            #6. update processed count
            files_processed.append(f)

        except Exception:
            logging.exception(f"Failed to extract {f}. {files_processed} Processed", exc_info=True)
            raise

    logging.info(f"Extracted {len(files_processed)} files to staging directory.")
    
    return files_processed