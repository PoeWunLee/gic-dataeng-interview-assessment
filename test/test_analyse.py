import pytest
from pathlib import Path
import pandas as pd
import sqlite3
from src.analytics import analyse_data

#fixture for connection
@pytest.fixture
def make_connection(tmp_path:Path):
    """Fixture for temporary testing DB"""
    conn=sqlite3.connect(tmp_path/"test.db")
    yield conn
    conn.commit()
    conn.close()

@pytest.fixture
def make_tables(make_connection):
    """Fixture for creation and initialising table"""
    with make_connection as cnxn:
        ctx = cnxn.cursor()
        ctx.executescript("""
        DROP TABLE IF EXISTS "bond_reference";
        CREATE TABLE IF NOT EXISTS "bond_reference" (
            "SECURITY NAME"	TEXT,
            "ISIN"	TEXT,
            "SEDOL"	TEXT,
            "COUNTRY"	TEXT,
            "COUPON"	REAL,
            "MATURITY DATE"	TEXT,
            "COUPON FREQUENCY"	TEXT,
            "SECTOR"	TEXT,
            "CURRENCY"	TEXT
        );
        DROP TABLE IF EXISTS "bond_prices";
        CREATE TABLE IF NOT EXISTS "bond_prices" (
            "DATETIME"	TEXT,
            "ISIN"	TEXT,
            "PRICE"	REAL
        );
        DROP TABLE IF EXISTS "equity_reference";
        CREATE TABLE IF NOT EXISTS "equity_reference" (
            "SYMBOL"	TEXT,
            "COUNTRY"	TEXT,
            "SECURITY NAME"	TEXT,
            "SECTOR"	TEXT,
            "INDUSTRY"	TEXT,
            "CURRENCY"	TEXT
        );
        DROP TABLE IF EXISTS "equity_prices";
        CREATE TABLE IF NOT EXISTS "equity_prices" (
            "DATETIME"	TEXT,
            "SYMBOL"	TEXT,
            "PRICE"	REAL
        );
        DROP TABLE IF EXISTS "fund_position";
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
        """)
        ctx.close()

@pytest.fixture
def make_data(make_connection, make_tables):
    """Fixture for inserting dummy data"""
    make_tables

    #insert statements
    fund_sql = f"""INSERT INTO fund_position
        ("FINANCIAL TYPE","SYMBOL","SECURITY NAME","SEDOL","PRICE","QUANTITY","REALISED P/L","MARKET VALUE","FUND","DATETIME")
        VALUES
        ('Equities','HSIC','Henry Schein',NULL,1000,8510.06783025756,-2606.5467800899837,582599.2436594325,'Applebead','2022-10-31'),
        ('Government Bond','US912810FS25','FIN-TSY INFL IX N/B 2% 01/15/2026','BZ56W67',1000,7442.575996742709,-577.4285587510394,1203315.6871533613,'Applebead','2022-10-31')
        """
    eq_price_sql = """INSERT INTO equity_prices ("DATETIME", "SYMBOL", "PRICE") VALUES ('2022-10-31', 'HSIC', 1000)"""
    bond_price_sql = """INSERT INTO bond_prices ("DATETIME", "ISIN", "PRICE") VALUES ('2022-10-31', 'US912810FS25', 1000)"""
    bond_ref_sql = """INSERT INTO "bond_reference" ("SECURITY NAME","ISIN","SEDOL","COUNTRY","COUPON","MATURITY DATE","COUPON FREQUENCY","SECTOR","CURRENCY") VALUES ('TSY INFL IX N/B 2% 01/15/2026','US912810FS25','BZ56W67','US',2.0,'15/01/2026','every 6 month','Treasury','USD')"""
    eq_ref_sql = """INSERT INTO "equity_reference" ("SYMBOL","COUNTRY","SECURITY NAME","SECTOR","INDUSTRY","CURRENCY") VALUES ('HSIC','US','Henry Schein','Health Care','Health Care Distributors','USD')"""
    sql_compiled = ";".join([fund_sql,eq_price_sql, eq_ref_sql, bond_price_sql, bond_ref_sql])

    #execute insert statements
    with make_connection as conn:
        ctx = conn.cursor()
        ctx.executescript(sql_compiled)
        ctx.close()

@pytest.fixture
def make_dir(tmp_path:Path, input_sql:str):
    """Fixture to create directories and sql file"""
    #make output directory
    tmp_dirs=[tmp_path/"sql", tmp_path/"data"/"analytics"]
    for dir in tmp_dirs:
        dir.mkdir(parents=True,exist_ok=True)
    
    #make_sql_file
    with open(tmp_dirs[0]/"test_sql.sql", 'w') as f:
        f.write(input_sql)

    return tmp_dirs

@pytest.mark.parametrize(
    "input_sql,output_results",
    [
        (
            "SELECT COUNT(*) FROM fund_position;"
            ,2
        ),
        (
            "SELECT SUM(PRICE) FROM fund_position;"
            ,2000.0
        ),
        (
            """SELECT fp.PRICE-ep.PRICE FROM fund_position fp join equity_prices ep on ep.SYMBOL=fp.SYMBOL and fp.DATETIME=ep.DATETIME ;"""
            ,0
        ),
        (
            """SELECT fp.PRICE-bp.PRICE FROM fund_position fp join bond_prices bp on bp.ISIN=fp.SYMBOL and fp.DATETIME=bp.DATETIME ;"""
            ,0
        ),

        (
            """SELECT "SECURITY NAME" FROM bond_reference WHERE SEDOL='BZ56W67';"""
         , "TSY INFL IX N/B 2% 01/15/2026"
        ),
        (
            """SELECT "SECURITY NAME" FROM equity_reference WHERE SYMBOL='HSIC'"""
            , 'Henry Schein'
        )
    ]
)
def test_analyse_data(input_sql:str, output_results:str|int|float, tmp_path:Path,make_dir, make_data):
    """Unit testing for various sql commands executed"""
    #arrange - initialise DB, create tables, insert dummy data. provide input and output filepaths for function
    make_data
    sql_root_path, export_root_path=make_dir
    sql_filepath, export_filepath = sql_root_path/"test_sql.sql", export_root_path/"test_csv.csv"
    config_dict = {"test_analysis":{sql_filepath:export_filepath}}

    #act - execute sql query/analysis
    analyse_data(str(tmp_path/"test.db"), config_dict, sql_root_path, export_root_path)

    #assert
    res_df = pd.read_csv(export_filepath)
    assert res_df.iloc[:,0].to_list()==[output_results]