# Overview
This code repository is a submission for GIC Data Engineer take-home assessment.

## Getting Started
1. Clone this repo to local
    ```
    git clone https://github.com/PoeWunLee/gic-dataeng-interview-assessment.git 
    ```

2. Navigate to the root directory (gic-dataeng-interview-assessment), initialise a venv
    ```
    cd gic-dataeng-interview-assessment
    python -m venv .venv
    ```

3. Install required dependencies and packages from pyproject.toml (pip or poetry)
    ```
    pip install .
    poetry install
    ```

4. Create an .env file and initialise DB connection string env variabled name CNXN_STR.<br/>For the scope of this assessment, sqlite3 is used and CNXN_STR is set to a .db filename (e.g. 'gic.db')<br/>

    Powershell:
    ```
    New-Item -Path .env -ItemType File -Value "CNXN_STR='gic.db'"
    ```
    Bash:
    ```
    echo "CNXN_STR='gic.db'" > .env
    ```

## Usage
main.py is the main entry point of this project. To trigger the load of fund position, run the following in terminal.
```
python main.py
```
## Unit Testing
The pytest suite is used for unit testing of the src functions for each step of the ETL.

To invoke pytest, simply run in root directory (~/gic-dataeng-interview-assessment)
```
pytest
```

or run individual pytest 
```
pytest test/test_extract.py
pytest test/test_load.py
pytest test/test_analyse.py
```

## Design Details
1. `main.py`
Main entrypoint for the project to perform all operations (initialise, extract, load, analyse) run via command line.

2. `src/`
```
├───src
│   │   analytics.py
│   │   extract_data.py
│   │   init_tables.py
│   │   load_data.py
│   │   __init__.py
```
Each file in this directory is an abstraction of each step in the ETL. 
- `init_tables.py`: Initialise tables (reference and fund postion) within the sqlite3 DB.
- `extract_data.py`: Extract raw funds CSV to staging directory, with enrichment of metadata (fundname and date) in content of CSV.
- `load_data.py`: Load all CSV files from staging area to sqlite3 DB into fund_position table
- `analytics.py`: Perform fund reconciliation and best performing fund analyses, exporting the results as CSV.

3. `data/`
```
├───data
│   ├───raw
│   │       Applebead.28-02-2023 breakdown.csv
│   │       Belaware.28_02_2023.csv
│   │       Fund Whitestone.28-02-2023 - details.csv
│   │ 			...
│   │ 
│   ├───staging
│   │    ├───2022-08-31
│   │    │       Applebead.csv
│   │    │       Belaware.csv
│   │    │ 		...
│	│	 │	...
│   │    └───2023-08-31
│   │           Applebead.csv
│   │           Belaware.csv
│   │     		
│   └───analytics
│   │       mthly_top_performing_fund.csv
│   │       recon_price_breakdown_by_symbol.csv
│   │       recon_price_summary.csv
│   │
```
Repository of all data files that are involved in the ETL.
- `/raw/`: First landing directory of raw fund CSVs.
- `/staging/`: Staged files post extaction and processing from extract step. Contains subdirectories partitioned by date in YYYY-MM-DD (for future efficient loading from stage to DB)
- `/analytics/`: Exports of reconciliation analysis between funds vs reference price (summary and symbol level available) and analysis of monthly best performing funds.

4. `sql/`
```
├───sql
│   │  best-performing-fund.sql
│   │  fund-position.sql
│   │  master-reference-sql.sql
│   │  reconciliation-query-breakdown.sql
│   │  reconciliation-query-summary.sql
```
Contains sql scripts for execution. Includes DDL for table initiation, as well as select queries for analytics step.

5. `utils/`
```
└───utils
    │   db_utils.py
    │   file_utils.py
    │   log_utils.py
    │   metadata_utils.py
    │   __init__.py
```
Common utility scripts used and imported from other scripts in this repository, such as DB connection utilities.

6. `test/`
```
├───test
│   │   test_analyse.py
│   │   test_extract.py
│   │   test_load.py
│   │   __init__.py
```
Directory containing unit testing for key functions and components of the repository. Namely load, extract and analyse.

## Assumptions/Scope of take-home submission

1. Incoming Funds Data 
- arrives monthly and consistent as CSV file format
- file structure and naming are consistent across months
- filenames will always have EOM date (with year, month, day details) and fund name
- for a given month, each fund only has one csv file. Files are not resent or duped.

2. Reference data
- all insturments and symbols in incoming data are available in master reference dataset
- master reference dataset is assumed to be clean and complete for pricing

3. Fund coverage
- submission covers the scope for N datasets. logic to onboarding/decomm metadata of new funds beyond the 10 funds in this submission is out of scope.

4. Pricing/Valuation
- utilising most recent available price data, prior to the specified date should there be gaps

5. Execution of the solution
- assumed to be run locally without orchestration/scheduling or production deployments

## Notes on known potential feature enhancements
1. Extract
- Logic to skip erronous file while continuing to extract others
- Incremental ingestion and handling
- Produce extract report/extract history
2. Load
- Load by specific date partitions
3. Analyse
- Enhancing to use pandas in post processing of SQL query from DB
4. Others
- Logic to continue subsequent steps when previous steps are failing in ```main.py```
- Option to run only certain operations while not others (e.g. only load) - potentially with command line arguments in main()
- Unit testing coverage on data related logic (e.g.results from analytics)