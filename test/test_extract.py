import pytest
from utils.metadata_utils import parse_raw_details, enrich_raw_df_with_details, parse_staging_pathname
from config.file_configs import PARSE_RAW_DETAILS_CONFIG
import pandas as pd

@pytest.mark.parametrize(
    "input_filename,output",
    [
        ("Applebead.28-02-2023 breakdown.csv",{"fund_name":"Applebead", "date_time":"28-02-2023"}),
        ("Belaware.30_06_2023.csv",{"fund_name":"Belaware", "date_time":"30_06_2023"}),
        ("Fund Whitestone.31-08-2022 - details.csv",{"fund_name":"Whitestone", "date_time":"31-08-2022"}),
        ("Leeder.04_30_2023.csv",{"fund_name":"Leeder", "date_time":"04_30_2023"}),
        ("mend-report Wallington.28_02_2023.csv",{"fund_name":"Wallington", "date_time":"28_02_2023"}),
        ("TT_monthly_Trustmind.20230831.csv",{"fund_name":"Trustmind","date_time":"20230831"}),
        ("Virtous.11-30-2022 - securities.csv",{"fund_name":"Virtous","date_time":"11-30-2022"}),
        ("Report-of-Gohen.04-30-2023.csv",{"fund_name":"Gohen" ,"date_time":"04-30-2023"}),
        ("Magnum.31-08-2023.csv",{"fund_name":"Magnum", "date_time":"31-08-2023"}),
        ("somegiberrish 31-08-2023.csv",{"fund_name":None, "date_time":"31-08-2023"}),
        ("gohen 31-08-2023.csv",{"fund_name":"gohen", "date_time":"31-08-2023"}),
        ("TT_monthly_Trustmind.202301.csv",{"fund_name":"Trustmind","date_time":None})
     
    ]
)
def test_parse_raw_details(input_filename, output):
    assert parse_raw_details(input_filename, PARSE_RAW_DETAILS_CONFIG)==output

@pytest.mark.parametrize(
    "input_fundname, input_date, output_results",
    [
        ("Applebead","28-02-2023", ["Applebead", pd.Timestamp("2023-02-28")]),
        ("Belaware", "30_06_2023", ["Belaware", pd.Timestamp("2023-06-30")]),
        ("Whitestone", "31-08-2022", ["Whitestone", pd.Timestamp("2022-08-31")]),
        ("Leeder", "04_30_2023", ["Leeder", pd.Timestamp("2023-04-30")]),
        ("Wallington","28_02_2023", ["Wallington", pd.Timestamp("2023-02-28")]),
        ("Trustmind","20230831", ["Trustmind", pd.Timestamp("2023-08-31")]),
        ("Virtous", "11-30-2022", ["Virtous", pd.Timestamp("2022-11-30")]),
        ("Gohen", "04-30-2023", ["Gohen", pd.Timestamp("2023-04-30")]),
        ("Magnum", "31-08-2023", ["Magnum", pd.Timestamp("2023-08-31")]),
        ("otherfundname", "30-09-1990", ["Otherfundname", pd.Timestamp("1990-09-30")])
    ]

)
def test_enrich_raw_df_with_details(input_fundname, input_date, output_results):
    #generate random df
    random_df = pd.DataFrame(["random_value"], columns=["random_col"])
    results_df = enrich_raw_df_with_details(random_df, input_fundname, input_date)
    results_fund = results_df["FUND"][0]
    results_date = results_df["DATETIME"][0]

    assert [results_fund, results_date]==output_results
