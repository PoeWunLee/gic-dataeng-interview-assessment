import pytest
#load scripts
from src.extract_data import extract_raw_to_stage
from src.load_data import load_funds
from src.init_tables import init_tables
from src.analytics import analyse_data
from src.etl import PipelineRun, PipelineStatus, PipelineOptions

from utils.configs_utils import Configs, InitialiseConfigs, ExtractConfigs, LoadConfigs, AnalyseConfigs
from utils.file_utils import get_paths, generate_dir

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

        "input_etl_run_options,input_fundname,input_date,output_status",
        [
            ({"init":True,"extract":True, "load":True, "analyse":True},"RandomFundname", "2025-08-31", {"init":1,"extract":1, "load":1,"analyse":1}),
            ({"init":True,"extract":False, "load":False, "analyse":False},"RandomFundname", "2025-08-31", {"init":1,"extract":0, "load":0,"analyse":0}),
            ({"init":True,"extract":True, "load":False, "analyse":False},"RandomFundname", "2025-08-31", {"init":1,"extract":1, "load":0,"analyse":0}),
            ({"init":True,"extract":False, "load":True, "analyse":False},"RandomFundname", "2025-08-31", {"init":1,"extract":0, "load":1,"analyse":0}),
            ({"init":True,"extract":False, "load":False, "analyse":True},"RandomFundname", "2025-08-31", {"init":1,"extract":0, "load":0,"analyse":1}),
            ({"init":True,"extract":True, "load":True, "analyse":False},"RandomFundname", "2025-08-31", {"init":1,"extract":1, "load":1,"analyse":0}),
            ({"init":True,"extract":True, "load":False, "analyse":True},"RandomFundname", "2025-08-31", {"init":1,"extract":1, "load":0,"analyse":1}),
            ({"init":True,"extract":False, "load":True, "analyse":True},"RandomFundname", "2025-08-31", {"init":1,"extract":0, "load":1,"analyse":1})
        
        ]
)
def test_etl(input_etl_run_options,input_fundname,input_date,output_status, tmp_path, make_configs):
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

    #4. in the case where extract is not run, create dummy staging file
    if not(input_etl_run_options["extract"]) and input_etl_run_options["load"]:
        #sub-dir
        staging_dir = paths["staging"]/"{}".format(input_date)

        #make sub directory
        generate_dir(staging_dir)

        with open(staging_dir/"{}.csv".format(input_fundname.upper()), 'w') as f:
            f.write("FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE,FUND,DATETIME\nEquities,HSIC,Henry Schein,,81.1,8508.375294889569,396.05327610977776,690029.236415544,{},{}".format(input_fundname, input_date))

    #initialisation of files etc
    run_options = PipelineOptions(
        is_init=input_etl_run_options["init"],
        is_extract=input_etl_run_options["extract"],
        is_load=input_etl_run_options["load"],
        is_analyse=input_etl_run_options["analyse"] 
    )
    pipeline = PipelineRun(run_options=run_options,configs=configs, paths=paths)
    status = pipeline.run(target_date=input_date, target_fund=input_fundname)

    assert status.init_status==output_status["init"]
    assert status.extract_status==output_status["extract"]
    assert status.loaded_status==output_status["load"]
    assert status.analyse_status==output_status["analyse"]


@pytest.mark.parametrize(

        "input_fundname_datetime,input_target_date,output_status",
        [
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2026-02-28', {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2025-08-31', {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '2025-09-30', {"init":1,"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], None, {"init":1,"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '20250831', {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '31-08-2025', {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], '31/08/2025', {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], ['31/08/2025', '20260228'], {"init":1,"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"], ["RandomFundname", "20230226"]], ['31/08/2025', '20260228'], {"init":1,"extract":3, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"], ["RandomFundname", "20230226"]], ['2027-09-30'], {"init":1,"extract":3, "load":0,"analyse":1})
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

    #act
    run_options = PipelineOptions(is_init=True,is_extract=True,is_load=True,is_analyse=True)
    pipeline = PipelineRun(run_options=run_options,configs=configs, paths=paths)
    status = pipeline.run(target_date=input_target_date)

    assert status.init_status==output_status["init"]
    assert status.extract_status==output_status["extract"]
    assert status.loaded_status==output_status["load"]
    assert status.analyse_status==output_status["analyse"]

@pytest.mark.parametrize(

        "input_fundname_datetime,input_target_fund,output_status",
        [
      
            ([["RandomFundname", "2025-08-31"], ["RandomFundname", "2026-02-28"]], None, {"init":1,"extract":2, "load":2,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "SomeOtherFundname", {"init":1,"extract":2, "load":1,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "RandomFundname", {"init":1,"extract":2, "load":1,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "FundNameExample", {"init":1,"extract":2, "load":0,"analyse":1}), #-
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "randomfundname", {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], "FundnameNotRegisteredInConfig", {"init":1,"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["FundnameNotRegisteredInConfig"], {"init":1,"extract":2, "load":0,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["someotherfundname","FundnameNotRegisteredInConfig"], {"init":1,"extract":2, "load":1,"analyse":1}),
            ([["RandomFundname", "2025-08-31"], ["SomeOtherFundname", "2026-02-28"]], ["randomfundname","SOMEOTHERFUNDNAME"], {"init":1,"extract":2, "load":2,"analyse":1})
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
    run_options = PipelineOptions(is_init=True,is_extract=True,is_load=True,is_analyse=True)
    pipeline = PipelineRun(run_options=run_options,configs=configs, paths=paths)
    status = pipeline.run(target_fund=input_target_fund)

    assert status.init_status==output_status["init"]
    assert status.extract_status==output_status["extract"]
    assert status.loaded_status==output_status["load"]
    assert status.analyse_status==output_status["analyse"]