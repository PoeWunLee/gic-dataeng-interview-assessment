from __future__ import annotations
import sqlite3
from sqlite3 import Connection
from typing import Generator
from pathlib import Path
from contextlib import contextmanager
import sys

ROOT_DIR = Path(__file__).parent.parent.absolute()
DB_ASSETS_DIR = ROOT_DIR / "db"

sys.path.append(ROOT_DIR)

from configs.db_configs import DB_HOST

@contextmanager
def init_db_connect(cnxn_str:str=DB_HOST)->Generator[Connection, None, None]:
    """Initialise database connection and cursor to local sqlite3 - ensure clean commits and rollback. 
    Creates db if not yet exists."""
    
    #initialise conn value
    conn=None
    try:
        conn = sqlite3.connect(cnxn_str)
        yield conn
    except Exception:
        if conn:
            conn.rollback()
        raise 
    finally:
        if conn:
            conn.close()