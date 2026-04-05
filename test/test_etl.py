import pytest
#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data
from src.etl import PipelineRun, PipelineStatus

from utils.configs_utils import Configs, InitialiseConfigs, ExtractConfigs, LoadConfigs, AnalyseConfigs
from utils.file_utils import get_paths

@pytest.fixture
def make_configs():
    cnxn_str = "test.db"
    raw_filename_ext = "*.csv"
    staging_filename_ext="*.csv"
    parse_raw_details_config = {
        "fund_name":"randomfundname|someotherfundname|fundnamexample" ,
        "date_time":r"\d{8}|\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}_\d{2}_\d{4}|\d{4}_\d{2}_\d{2}"
    }
    fund_table_name = "test_table"
    init_db_scripts = {"test":f"{fund_table_name}.sql"}
    analytics_input_output_dict = {
        "test analyse":{"test_analyse.sql":"test_analyse.csv"}
    }

    init_configs = InitialiseConfigs(cnxn_str, init_db_scripts)
    extract_configs = ExtractConfigs(raw_filename_ext, parse_raw_details_config)
    load_configs = LoadConfigs(cnxn_str, staging_filename_ext, fund_table_name)
    analyse_configs = AnalyseConfigs(cnxn_str,analytics_input_output_dict)

    configs = Configs(init_configs, extract_configs, load_configs, analyse_configs)

    return configs


@pytest.mark.parametrize(

        "input_fundname,input_date,output_status",
        [
            ("RandomFundname", "2025-08-31", {"extract":1, "load":1,"analyse":1})
        
        ]
)
def test_etl(input_fundname,input_date,output_status, tmp_path, make_configs):
    #arrange
    configs=make_configs
    paths = get_paths(tmp_path)

    #create tmp files
    # 1. raw file
    with open(paths['raw']/f'{input_fundname}_{input_date}.csv','w') as f:
        f.write("FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\nEquities,HSIC,Henry Schein,,81.1,8508.375294889569,396.05327610977776,690029.236415544")

    #2. init sql table scripts
    with open(paths["sql"]/f'{configs.load_configs.fund_table_name}.sql','w') as f:
        f.write(f"""BEGIN TRANSACTION;
        DROP TABLE IF EXISTS "{configs.load_configs.fund_table_name}";
        CREATE TABLE IF NOT EXISTS "{configs.load_configs.fund_table_name}" (
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
        COMMIT;""")

    #3 . init sql analyses scripts
    with open(paths["sql"]/'test_analyse.sql','w') as f:
        f.write("SELECT 1;")

    #initialisation of files etc
    pipeline = PipelineRun(configs, paths, is_init=True)
    status = pipeline.run(target_date=input_date)
    assert status.extract_status==output_status["extract"]
    assert status.loaded_status==output_status["load"]
    assert status.analyse_status==output_status["analyse"]


@pytest.mark.parametrize(

        "input_fundname_datetime,input_target_date,output_status",
        [
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2026-02-28', {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2025-08-31', {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2025-09-30', {"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], None, {"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '20250831', {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '31-08-2025', {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '31/08/2025', {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], ['31/08/2025', '20260228'], {"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"], ["RandomFundname", "20230226"]], ['31/08/2025', '20260228'], {"extract":3, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"], ["RandomFundname", "20230226"]], ['2027-09-30'], {"extract":3, "load":0,"analyse":1})
        ]
)
def test_etl_date_load(input_fundname_datetime,input_target_date,output_status, tmp_path, make_configs):
    #arrange
    paths = get_paths(tmp_path)
    configs=make_configs

    #create tmp files
    for inputs in input_fundname_datetime:
        input_fundname, input_date = inputs[0], inputs[1]

        # 1. raw file
        with open(paths['raw']/f'{input_fundname}_{input_date}.csv','w') as f:
            f.write("FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\nEquities,HSIC,Henry Schein,,81.1,8508.375294889569,396.05327610977776,690029.236415544")

        #2. init sql table scripts
        with open(paths["sql"]/f'{configs.load_configs.fund_table_name}.sql','w') as f:
            f.write(f"""BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "{configs.load_configs.fund_table_name}";
            CREATE TABLE IF NOT EXISTS "{configs.load_configs.fund_table_name}" (
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
            COMMIT;""")

        #3 . init sql analyses scripts
        with open(paths["sql"]/'test_analyse.sql','w') as f:
            f.write("SELECT 1;")

    #assert
    pipeline = PipelineRun(configs, paths, is_init=True)
    status = pipeline.run(target_date=input_target_date)

    expected_output = PipelineStatus(output_status["extract"], output_status["load"], output_status["analyse"]) 

    assert status==expected_output
@pytest.mark.parametrize(

        "input_fundname_datetime,input_target_fund,output_status",
        [
      
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], None, {"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "SomeOtherFundname", {"extract":2, "load":1,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "RandomFundname", {"extract":2, "load":1,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "FundNameExample", {"extract":2, "load":0,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "randomfundname", {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "FundnameNotRegisteredInConfig", {"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["FundnameNotRegisteredInConfig"], {"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["someotherfundname","FundnameNotRegisteredInConfig"], {"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["randomfundname","SOMEOTHERFUNDNAME"], {"extract":2, "load":2,"analyse":1})
        ]
)
def test_etl_fundname_load(input_fundname_datetime,input_target_fund,output_status, tmp_path, make_configs):
    #arrange
    paths = get_paths(tmp_path)
    configs=make_configs

    #create tmp files
    for inputs in input_fundname_datetime:
        input_fundname, input_date = inputs[0], inputs[1]

        # 1. raw file
        with open(paths['raw']/f'{input_fundname}_{input_date}.csv','w') as f:
            f.write("FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\nEquities,HSIC,Henry Schein,,81.1,8508.375294889569,396.05327610977776,690029.236415544")

        #2. init sql table scripts
        with open(paths["sql"]/f'{configs.load_configs.fund_table_name}.sql','w') as f:
            f.write(f"""BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "{configs.load_configs.fund_table_name}";
            CREATE TABLE IF NOT EXISTS "{configs.load_configs.fund_table_name}" (
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
            COMMIT;""")

        #3 . init sql analyses scripts
        with open(paths["sql"]/'test_analyse.sql','w') as f:
            f.write("SELECT 1;")

    #assert
    pipeline = PipelineRun(configs, paths, is_init=True)
    status = pipeline.run(target_fund=input_target_fund)

    expected_output = PipelineStatus(output_status["extract"], output_status["load"], output_status["analyse"]) 

    assert status==expected_output