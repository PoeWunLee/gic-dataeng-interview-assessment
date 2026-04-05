from pathlib import Path
import pandas as pd
from typing import Generator
import os
import logging

##Generic##
def get_files(dir:Path, ext:str, filter_files:set[str]|list[str]|None=None)->list[Path]:
    "Retrieve all files of a particular extension in a directory path recursively"
    if filter_files:
        return [f for f in dir.rglob(ext) if f.name in set(filter_files)]
    return [f for f in dir.rglob(ext)]

def generate_dir(filepath:Path) -> None:
    """Generate directory if does not exist. If exists, exception not raised"""
    if not os.path.exists(filepath):
        os.makedirs(filepath, exist_ok=True)
    return

#parsing paths
def get_paths(root:Path)->dict[str,Path]:
    """Parse all paths in a dictionary to be passed into each pipeline step"""

    directories = {
        "root":root,
        "raw":root / "data" / "raw",
        "staging":root / "data" / "staging",
        "sql":root / "sql",
        "analytics":root / "data" / "analytics",
        "config":root / "config"
    }

    #initialise directories if doesn't exist
    for d in directories.values():
        generate_dir(d)
    
    return directories

##CSV##
def extract_csv_to_df(filename:str)->pd.DataFrame|None:
    """Parse CSV rows to dataframe format"""
    extract_df = pd.read_csv(filename, header=0)
    return extract_df

def save_df_to_csv(df:pd.DataFrame, filepath:Path)->None:
    """Export dataframe records and fields to CSV with specified dir"""
    df.to_csv(filepath, index=False)
    return

##SQL File##
def extract_sql_from_file(filepath:Path)->str:
    """Extract sql from .sql file. Ensures utf-8 encoding."""
    with open(filepath, 'r', encoding="utf-8") as sqlfile:
        sql_statement = sqlfile.read()
    return sql_statement