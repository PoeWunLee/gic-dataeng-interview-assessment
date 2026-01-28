import pytest
from pathlib import Path
from utils.metadata_utils import parse_raw_details, enrich_raw_df_with_details, parse_staging_pathname
from config.file_configs import PARSE_RAW_DETAILS_CONFIG
from src.extract_data import extract_raw_to_stage
import pandas as pd

##Unit Testing of main extract step
@pytest.fixture
def make_dirs(tmp_path:Path)->dict[str:Path]:
    """Fixture to create tmp directories for raw and staging"""
    path_dict = {
        "raw": tmp_path/"raw",
        "staging":tmp_path/"staging"
    }

    for p in path_dict.values():
        p.mkdir(parents=True, exist_ok=True)

    return path_dict

@pytest.fixture
def make_csv(make_dirs:dict[str:Path], input_filename:str):
    """Fixture to create raw csv file"""
    raw_csv = make_dirs["raw"] / input_filename
    with open(raw_csv, 'w') as r:
        r.write(
        """FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\n
        Equities,TJX,TJX Companies,,75.98,37468.4207623162,14761.023496753585,2846850.609520785"""
        )
    
    return raw_csv

@pytest.mark.parametrize(
    "input_filename,output",
    [
        ("Applebead.28-02-2023 breakdown.csv",{"fund":"Applebead", "date_time_partition":"2023-02-28"}),
        ("Belaware.30_06_2023.csv",{"fund":"Belaware", "date_time_partition":"2023-06-30"}),
        ("Fund Whitestone.31-08-2022 - details.csv",{"fund":"Whitestone", "date_time_partition":"2022-08-31"}),
        ("Leeder.04_30_2023.csv",{"fund":"Leeder", "date_time_partition":"2023-04-30"}),
        ("mend-report Wallington.28_02_2023.csv",{"fund":"Wallington", "date_time_partition":"2023-02-28"}),
        ("TT_monthly_Trustmind.20230831.csv",{"fund":"Trustmind","date_time_partition":"2023-08-31"}),
        ("Virtous.11-30-2022 - securities.csv",{"fund":"Virtous","date_time_partition":"2022-11-30"}),
        ("Report-of-Gohen.04-30-2023.csv",{"fund":"Gohen" ,"date_time_partition":"2023-04-30"}),
        ("Magnum.31-08-2023.csv",{"fund":"Magnum", "date_time_partition":"2023-08-31"}),
        ("gohen 31-08-2023.csv",{"fund":"Gohen", "date_time_partition":"2023-08-31"})
     
    ]
)
def test_extract_raw_to_stage(input_filename, output,tmp_path, make_dirs, make_csv):
    """Testing main extract function"""
    #arrange for tmp dir
    csv_path = make_csv
    staging_root_path = make_dirs["staging"]

    #act
    extract_raw_to_stage([csv_path], staging_root_path, PARSE_RAW_DETAILS_CONFIG)
    
    #assert staging path is generatec correctly
    staged_file=staging_root_path/output["date_time_partition"]/ "{}.csv".format(output["fund"])
    assert staged_file.exists()

    #assert metadata is enriched
    results_df = pd.read_csv(staged_file)
    assert results_df["FUND"].iloc[0] == output["fund"]
    assert results_df["DATETIME"].iloc[0] == output["date_time_partition"]


##Unit Testing of key inidivdual utils step
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
        ("Applebead","28-02-2023", ["Applebead", "28-02-2023"]),
        ("Belaware", "30_06_2023", ["Belaware", "30_06_2023"]),
        ("Whitestone", "31-08-2022", ["Whitestone", "31-08-2022"]),
        ("Leeder", "04_30_2023", ["Leeder", "04_30_2023"]),
        ("Wallington","28_02_2023", ["Wallington", "28_02_2023"]),
        ("Trustmind","20230831", ["Trustmind", "20230831"]),
        ("Virtous", "11-30-2022", ["Virtous", "11-30-2022"]),
        ("Gohen", "04-30-2023", ["Gohen", "04-30-2023"]),
        ("Magnum", "31-08-2023", ["Magnum", "31-08-2023"]),
        ("otherfundname", "30-09-1990", ["Otherfundname", "30-09-1990"])
    ]

)
def test_enrich_raw_df_with_details(input_fundname, input_date, output_results):
    #generate random df
    random_df = pd.DataFrame(["random_value"], columns=["random_col"])
    #act
    results_df = enrich_raw_df_with_details(random_df, input_fundname, input_date)
    results_fund = results_df["FUND"].unique()[0]
    results_date = results_df["DATETIME"].unique()[0]
    #assert
    assert [results_fund, results_date]==output_results

