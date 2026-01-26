import pytest
from utils.metadata_utils import parse_raw_details, enrich_raw_df_with_details, parse_staging_pathname
from config.file_configs import PARSE_RAW_DETAILS_CONFIG

@pytest.mark.parametrize(
    "input_filename,input_config,output",
    [
        ("Applebead.28-02-2023 breakdown.csv",PARSE_RAW_DETAILS_CONFIG ,{"fund_name":"Applebead", "date_time":"28-02-2023"}),
        ("TT_monthly_Trustmind.20230831.csv",PARSE_RAW_DETAILS_CONFIG,{"fund_name":"Trustmind","date_time":"20230831"}),
        ("Report-of-Gohen.04-30-2023.csv",PARSE_RAW_DETAILS_CONFIG,{"fund_name":"Gohen" ,"date_time":"04-30-2023"}),
        ("Magnum.31-08-2023.csv",PARSE_RAW_DETAILS_CONFIG ,{"fund_name":"Magnum", "date_time":"31-08-2023"}),
        ("somegiberrish 31-08-2023.csv",PARSE_RAW_DETAILS_CONFIG ,{"fund_name":None, "date_time":"31-08-2023"}),
        ("gohen 31-08-2023.csv",PARSE_RAW_DETAILS_CONFIG ,{"fund_name":"gohen", "date_time":"31-08-2023"}),
        ("TT_monthly_Trustmind.202301.csv",PARSE_RAW_DETAILS_CONFIG,{"fund_name":"Trustmind","date_time":None})
     
    ]
)
def test_parse_raw_details(input_filename, input_config, output):
    assert parse_raw_details(input_filename, input_config)==output