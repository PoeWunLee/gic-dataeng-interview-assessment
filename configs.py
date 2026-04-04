import os
from dotenv import load_dotenv

#load environment variable
load_dotenv()

#all config variables
CNXN_STR=os.getenv("CNXN_STR")
RAW_FILENAME_EXT = "*.csv"
STAGING_FILENAME_EXT = "*.csv"
PARSE_RAW_DETAILS_CONFIG = {
    "fund_name":r"applebead|belaware|whitestone|leeder|magnum|wallington|gohen|catalysm|trustmind|virtous", 
    "date_time":r"\d{8}|\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}_\d{2}_\d{4}|\d{4}_\d{2}_\d{2}"
}
FUND_TABLE_NAME="fund_position"
INIT_DB_SCRIPTS = {
    "reference":"master-reference-sql.sql",
    "funds":"fund-position.sql"
}
ANALYTICS_INPUT_OUTPUT_DICT = {
    "Fund Reconciliation":{
        "reconciliation-query-breakdown.sql":"recon_price_breakdown_by_symbol.csv",
        "reconciliation-query-summary.sql":"recon_price_summary.csv"
    },
    "Best Performing Fund":{
        "best-performing-fund.sql":"mthly_top_performing_fund.csv"
    }
}

