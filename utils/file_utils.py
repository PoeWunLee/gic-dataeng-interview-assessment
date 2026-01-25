from pathlib import Path
import pandas as pd
from typing import Generator
import logging
import os

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def get_files(dir:Path, ext:str)->Generator:
    "Retrieve all files of a particular extension in a directory path"
    return dir.glob(ext)

def generate_dir(filepath:Path) -> None:
    """Generate directory if does not exist"""
    if not os.path.exists(filepath):
        os.makedirs(filepath)
        logger.info(f"Created directory {filepath}")
    return
    
def extract_csv_to_df(filename:str)->pd.DataFrame|None:
    try:
        extract_df = pd.read_csv(filename, header=0)
        return extract_df
    except Exception:
        logger.exception(f"Converting CSV {filename} to DataFrame failed.")
        raise

def save_df_to_csv(df:pd.DataFrame, filepath:Path)->None:
    try:
        df.to_csv(filepath, index=False)
    except Exception:
        logger.exception(f"Exporting DataFrame to {filepath} failed.")
        raise