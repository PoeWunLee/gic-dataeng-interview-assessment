import pytest
from pathlib import Path
import sys
from datetime import datetime

CURRENT_FILE_DIR=Path(__file__).parent.parent.absolute()
sys.path.append(CURRENT_FILE_DIR)

from utils.file_utils import get_details_from_filename
from src.extract_data import parse_raw_details, parse_datetime_format
from config.file_configs import PARSE_RAW_DETAILS_CONFIG
REGEX_FUNDNAME = PARSE_RAW_DETAILS_CONFIG["fund_name"]
REGEX_DATETIME = PARSE_RAW_DETAILS_CONFIG["date_time"]

@pytest.mark.parametrize(
    "input_filename, input_regex,input_tag,output",
    [
        ("Applebead.28-02-2023 breakdown.csv", REGEX_DATETIME, 'datetime', "28-02-2023"),
        ("somegibberish.28022023 breakdown.csv",REGEX_DATETIME, 'datetime', "28022023"),
        ("somegibberish.28_02_2023 breakdown.csv",REGEX_DATETIME, 'datetime', "28_02_2023"),
         ("somegibberish breakdown.csv",REGEX_DATETIME, 'datetime', None)
     
    ]
)
def test_get_date_from_filename(input_filename, input_regex,input_tag, output):
    assert get_details_from_filename(input_filename, input_regex,input_tag)==output

@pytest.mark.parametrize(
    "input_filename,input_config,output_fundname, output_date",
    [
        ("Applebead.28-02-2023 breakdown.csv",PARSE_RAW_DETAILS_CONFIG ,"Applebead", "28-02-2023"),
        ("TT_monthly_Trustmind.20230831.csv",PARSE_RAW_DETAILS_CONFIG,"Trustmind","20230831"),
        ("Report-of-Gohen.04-30-2023.csv",PARSE_RAW_DETAILS_CONFIG,"Gohen" ,"04-30-2023"),
         ("Magnum.31-08-2023.csv",PARSE_RAW_DETAILS_CONFIG ,"Magnum", "31-08-2023")
     
    ]
)
def test_parse_raw_details(input_filename, input_config,output_fundname, output_date):
    assert parse_raw_details(input_filename, input_config)==(output_fundname, output_date)

@pytest.mark.parametrize(
    "input_datetime,output_datetime",
    [
        ("28-02-2023", "2023-02-28"),
        ("20190223","2019-02-23"),
        ("28_02_2023","2023-02-28"),
        ("31-08-2023", "2023-08-31"),
        ("09-30-2023", "2023-09-30"),
        ("02_28_2023","2023-02-28"),
     
    ]
)
def test_parse_datetime_format(input_datetime,output_datetime):
    result_datetime = parse_datetime_format(input_datetime).strftime("%Y-%m-%d")
    assert result_datetime==output_datetime


# @pytest.mark.parametrize(
#     "test_input,output",
#     [
#         ("Applebead.28-02-2023 breakdown.csv", "applebead"),
#         ("somegibberish.28-02-2023 breakdown.csv", None)
     
#     ]
# )
# def test_get_fundname_from_filename(test_input, output):
#     assert get_fundname_from_filename(test_input)==output

# @pytest.mark.parametrize(
#     "test_input,output",
#     [
#         ("Applebead.28-02-2023 breakdown.csv", "28-02-2023"),
#         ("somegibberish.28022023 breakdown.csv", "28022023"),
#         ("somegibberish.28_02_2023 breakdown.csv", "28-02-2023"),
#          ("somegibberish breakdown.csv", None)
     
#     ]
# )
# def test_get_date_from_filename(test_input, output):
#     assert get_date_from_filename(test_input)==output