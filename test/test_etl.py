import pytest
from src.etl import PipelineRun, PipelineStatus
from utils.file_utils import get_paths, generate_dir
import shutil
from pathlib import Path
from utils.config_utils import InitialiseConfigs, ExtractConfigs, AnalyticsConfigs, LoadConfigs, ConfigsParser

@pytest.fixture
def make_paths(tmp_path:Path):
    paths = get_paths(tmp_path)
    return paths

@pytest.fixture
def make_configs():
    #get arbitrary configs
    fund_table_name="test_fund"
    init_db_scripts = {
        "testfund":"test_fund.sql"
    }
    raw_filename_ext = "*.csv"
    staging_filename_ext = "*.csv"
    parse_raw_details_config = {
        "fund_name":r"testfund", 
        "date_time":r"\d{8}|\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}_\d{2}_\d{4}|\d{4}_\d{2}_\d{2}"
    }
    analytics_input_output_dict = {
        "Random Test Name":{"random_test.sql":"random_test.csv"}
    }

    #parse configs
    init_configs = InitialiseConfigs(init_db_scripts=init_db_scripts)
    extract_configs = ExtractConfigs(raw_filename_ext=raw_filename_ext,parse_raw_details_config=parse_raw_details_config)
    load_configs= LoadConfigs(fund_table_name=fund_table_name, staging_filename_ext=staging_filename_ext)
    analytics_configs = AnalyticsConfigs(analytics_input_output_dict=analytics_input_output_dict)
    configs = ConfigsParser(init_configs, extract_configs,load_configs,analytics_configs)

    return configs

@pytest.fixture
def make_file_content():
    #dummy table creation
    return {
        "test_fund.sql":"""BEGIN TRANSACTION;
                DROP TABLE IF EXISTS "test_fund";
                CREATE TABLE IF NOT EXISTS "test_fund" (
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
                COMMIT;""",
        "random_test.sql":  """SELECT 1 from test_fund;""",
        "testfund_20250131.csv":"FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE\nEquities,TJX,TJX Companies,,78.19,38444.4378042699,-2899.9479114234236,3005970.5919158636,",
        "testfund.csv":"FINANCIAL TYPE,SYMBOL,SECURITY NAME,SEDOL,PRICE,QUANTITY,REALISED P/L,MARKET VALUE,FUND,DATETIME\nEquities,ATO,Atmos Energy,,110.54,1181.500062696657,209.884361218884,130603.0169304885,testfund,2022-08-31"
                }

@pytest.mark.parametrize(
    "input_args,output_count",
    [
        ({"init":False, "extract":False, "load":False, "analyse":False} ,{"extract":0, "load":0, "analyse":0}),
        ({"init":True, "extract":False, "load":False, "analyse":False},{"extract":0, "load":0, "analyse":0}),
        ({"init":True, "extract":True, "load":False, "analyse":False}, {"extract":1, "load":0, "analyse":0}),
        ({"init":True, "extract":True, "load":True, "analyse":False}, {"extract":1, "load":2, "analyse":0}), 
        ({"init":True, "extract":True, "load":True, "analyse":True}, {"extract":1, "load":2, "analyse":1}),
        ({"init":True, "extract":False, "load":True, "analyse":False}, {"extract":0, "load":1, "analyse":0}),
        ({"init":True, "extract":False, "load":False, "analyse":True}, {"extract":0, "load":0, "analyse":1})
    ]
)
def test_pipeline_funcs(input_args: dict[str, bool],
        output_count: dict[str, int], 
        tmp_path: Path,
        make_paths,
        make_configs,
        make_file_content
    ):

    #initialise paths, files and configs
    paths = make_paths
    file_content = make_file_content
    
    #arrange
    #csv
    with open(paths["raw"]/"testfund_20250131.csv", "w") as f:
        f.write(file_content["testfund_20250131.csv"])

    #init sql
    with open(paths["sql"]/"test_fund.sql", "w") as f:
        f.write(file_content["test_fund.sql"])
    #dummy staging file

    #staging csv
    generate_dir(paths["staging"]/"2022-08-31") #generate staging data dir
    with open(paths["staging"]/"2022-08-31"/"testfund.csv", "w") as f:
        f.write(file_content["testfund.csv"])
    
    #analytics sql
    with open(paths["sql"]/"random_test.sql", "w") as f:
        f.write(file_content["random_test.sql"])
    
    configs = make_configs
    cnxn_str = paths["root"] / "test.db"


    #act
    pipeline=PipelineRun(configs,input_args['init'], input_args['extract'], input_args['load'], input_args['analyse'])
    status = pipeline.run(path=paths, cnxn_str=cnxn_str)

    #assert
    assert status.extracted_files == output_count["extract"]
    assert status.loaded_files == output_count["load"]
    assert status.analysed_files == output_count["analyse"]