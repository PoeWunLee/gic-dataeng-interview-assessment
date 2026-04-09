import pytest
from pathlib import Path
from utils.config_utils import ConfigParser
from utils.file_utils import get_paths

from src.etl import run_pipeline
import itertools

@pytest.fixture
def make_configs(input_available_fundname:list[str],input_available_dates:list[str]):
    fundname_regex="|".join(input_available_fundname)
    return ConfigParser(
        raw_filename_ext="*.csv",
        staging_filename_ext="*.csv",
        parse_raw_details_config={
            "fund_name":fundname_regex,
            "date_time":r"\d{8}|\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}_\d{2}_\d{4}|\d{4}_\d{2}_\d{2}"
        },
        fund_table_name="test_table",
        init_db_scripts={"test":"test_init_script.sql"},
        analytics_input_output_dict={"test_analysis":{"test_analysis.sql":"test_results.csv"}},
        cnxn_str="test.db"
    )

@pytest.fixture
def make_paths(tmp_path:Path):
    return get_paths(tmp_path)
    
@pytest.fixture
def make_required_initial_file_content():
    # 1. raw csv
    raw_csv_content = "FINANCIAL TYPE,SYMBOL,SECURITY NAME,ISIN,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\nEquities,FICO,Fair Isaac,,883.59,82027.56352312499,364271.666506274,72478734.85339801"
    
    # 2. init sql
    init_sql_content = """BEGIN TRANSACTION;
        DROP TABLE IF EXISTS "test_table";
        CREATE TABLE IF NOT EXISTS "fund_position" (
            "FINANCIAL TYPE"    TEXT,
            "SYMBOL"    TEXT,
            "SECURITY NAME" TEXT,
            "SEDOL" TEXT,
            "ISIN" TEXT,
            "PRICE" REAL,
            "QUANTITY" REAL,
            "REALISED P/L" REAL,
            "MARKET VALUE" REAL,
            "FUND" TEXT,
            "DATETIME" TEXT
        );
        COMMIT;"""
    
    #3 . sql analysis
    analysis_sql_content = """SELECT FUND, DATETIME FROM test_table;"""

    return raw_csv_content,init_sql_content, analysis_sql_content 

@pytest.mark.parametrize(
    "input_available_fundname,input_available_dates,fund_args,date_args",
    [
        (["fundname1", "fundname2", "fundname3"], ["2025-08-31", "2026-01-31"], ["fundname1"], ["2025-08-31"]),
        (["fundname1", "fundname2"], ["2025-08-31", "2026-01-31"], ["fundname1", "fundname2"], ["2026-01-31"]),
    ]
)
def test_fund_date_inputs(input_available_fundname,
                          input_available_dates,
                          fund_args,
                          date_args,
                          make_configs,
                          make_paths,
                          make_required_initial_file_content,
                          tmp_path
                        ):
    #arrange
    configs=make_configs
    paths = make_paths
    raw_csv_content,init_sql_content, analysis_sql_content =make_required_initial_file_content

    #make csv
    filename_list=list(itertools.product(input_available_fundname, input_available_dates))
    expected_filename_list=list(itertools.product(fund_args, date_args))
    
    raw_files = [paths["raw"]/"{}{}".format("-".join(rf), configs.raw_filename_ext.replace("*", "")) for rf in filename_list]
    expected_raw_files = [paths["raw"]/"{}{}".format("-".join(rf), configs.raw_filename_ext.replace("*", ""))  for rf in expected_filename_list]
    for rf in raw_files:
        with open(rf,'w') as f:
            f.write(raw_csv_content)

    expected_staged_files = [paths["staging"]/f[1]/f"{f[0]}{configs.staging_filename_ext.replace('*','')}" for f in expected_filename_list]
    expected_analytics_files = [paths["analytics"]/configs.analytics_input_output_dict["test_analysis"]["test_analysis.sql"]]

    #make sqls
    
    # for sql_files,sql_statements in sql_objects.items():
    with open(paths["sql"]/configs.init_db_scripts.get("test"), 'w') as f:
        f.write(init_sql_content)
    
    test_sql_name = list(configs.analytics_input_output_dict["test_analysis"].keys())[0]
    with open(paths["sql"]/test_sql_name, 'w') as f:
        f.write(analysis_sql_content)
   
    # act
    extracted_files, loaded_data, analytics_output = run_pipeline(paths,configs,funds=fund_args, dates=date_args)
    
    # assert
    assert sorted(extracted_files)==sorted(expected_raw_files)
    assert loaded_data==sorted(expected_staged_files)
    assert analytics_output==sorted(expected_analytics_files)


    
