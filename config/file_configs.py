# Scaling & conformity considerations - consider yml/class based approach for recognition of each fund by its own format
RAW_FILENAME_EXT = "*.csv"
STAGING_FILENAME_EXT = ".csv"
PARSE_RAW_DETAILS_CONFIG = {
    "fund_name":r"applebead|belaware|whitestone|leeder|magnum|wallington|gohen|catalysm|trustmind|virtous", 
    "date_time":r"\d{8}|\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}_\d{2}_\d{4}|\d{4}_\d{2}_\d{2}"
}