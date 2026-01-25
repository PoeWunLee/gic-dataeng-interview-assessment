from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.absolute()
RAW_DIR=ROOT_DIR / "data" / "raw"
STAGING_DIR=ROOT_DIR / "data" / "staging"
CONFIG_DIR=ROOT_DIR / "config"

sys.path.append(CONFIG_DIR)
#print(sys.path)

from config.file_configs import PARSE_RAW_DETAILS_CONFIG, RAW_FILENAME_EXT
from utils.file_utils import get_files
from src.extract_data import extract_raw_to_stage


# def main()->None:
#     # 1. load data
#     raw_files = list_all_raw_files()
#     funds_df = extract_raw_csv(raw_files)

#     # 2. initialise db connection, ingest funds and reference
#     with init_db_connect() as cnxn:

#         load_funds(table_name="funds_df", conn=cnxn,funds_df=funds_df)

#         ctx = cnxn.cursor()
#         load_reference(ctx, CURRENT_FILE_DIR / "db" / "master-reference-sql.sql")
    
#     # 3. analyse data

def main():
    raw_files = get_files(RAW_DIR, RAW_FILENAME_EXT)
    #print(RAW_DIR)
    #print([f for f in raw_files])
    extract_raw_to_stage(raw_files, STAGING_DIR, PARSE_RAW_DETAILS_CONFIG)
    #print(report_df)

if __name__=="__main__":
    main()