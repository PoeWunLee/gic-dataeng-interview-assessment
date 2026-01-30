# Overview
This code repository is a submission for GIC Data Engineer take-home assessment.

## Getting Started
1. Clone this repo to local
    ```
    git clone https://github.com/PoeWunLee/gic-dataeng-interview-assessment.git 
    ```

2. Navigate to the root directory (~/gic-dataeng-interview-assessment)
    ```
    cd gic-dataeng-interview-assessment
    ```

3. (Optional) initialise and activate a virtual environment
    ```
    python -m venv .venv
    .venv/Scripts/activate
    ```

4. Install required dependencies and packages from pyproject.toml (pip or poetry)
    ```
    pip install .
    poetry install
    ```

5. Create an .env file and initialise DB connection string env variabled name CNXN_STR.<br/>For the scope of this assessment, sqlite3 is used and CNXN_STR is set to a .db filename (e.g. 'gic.db')<br/>

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
py main.py
python3 main.py
```

> [!NOTE]
> Depending on python installation, python command may be python/py/python3

Successful output display should look like the following

```
| INFO | 2026-01-30 09:59:08 | STARTED: [EXTRACT]
| INFO | 2026-01-30 09:59:09 | Extracted 130 files to staging directory. 
| INFO | 2026-01-30 09:59:09 | COMPLETED: [EXTRACT]

| INFO | 2026-01-30 09:59:09 | STARTED: [LOAD]
| INFO | 2026-01-30 09:59:13 | Loaded 10309 records into database table fund_position. 
| INFO | 2026-01-30 09:59:13 | COMPLETED: [LOAD]

| INFO | 2026-01-30 09:59:13 | STARTED: [ANALYTICS]
| INFO | 2026-01-30 09:59:19 | Fund Reconciliation analysis completed. Exported results to ['recon_price_breakdown_by_symbol.csv', 'recon_price_summary.csv']. 
| INFO | 2026-01-30 09:59:19 | Best Performing Fund analysis completed. Exported results to ['mthly_top_performing_fund.csv']. 
| INFO | 2026-01-30 09:59:19 | COMPLETED: [ANALYTICS]
```

## Unit Testing

> [!NOTE]
> - Unit tests are conducted for core pipeline logic i.e. extract, load and analyse, while other utility functions such as purely using third party libraries are omitted for practicality, and avoidance of overtesting. (e.g. connection initiation to DB with sqlite3 standard packages).
> - Some essential utilites in parsing metadata of fund name and date are also included in testing scope.
> - Note that at the juncture of this submission, data quality and query level checks are not included, but is considered as a future enhancement.

### Invoking Unit Testing
The pytest suite is used for this submisison. To invoke pytest, simply run in root directory (~/gic-dataeng-interview-assessment)
```
pytest
```
or run individual pytest 
```
pytest test/test_extract.py
pytest test/test_load.py
pytest test/test_analyse.py
```
in poetry syntax
```
poetry run python pytest
```
```
poetry run python pytest test/test_extract.py 
poetry run python pytest test/test_load.py
poetry run python pytest test/test_analyse.py
```

For verbose pytest output for each test case, add -vv arguments
```
pytest -vv
poetry run python pytest -vv
```

## Design Details

### High level pipeline flow
```
Raw CSVs
   ↓
Extract & Enrich
   ↓
Staging (partitioned by date)
   ↓
Load into SQLite
   ↓
Analytics Queries
   ↓
CSV Outputs
```

### Pipeline Components
1. Extract (`extract_data.py`)
    - Reads inconsistently named CSV fund file names.
    - Parses the following metadata from filenames:
        - fund name
        - date
    - Enriches each extract with these metdata, and writes them to staging partitioned by date sub-directories.

    Output: Extracted funds position in staging directory, partitioned by date 
    ```data/staging/<YYYY-MM-DD>/<fundname>.csv```

2. Load (`load_data.py`)
    - Reads staged CSVs.
    - Loads data into fund_position table in sqlite DB with a consistent schema.

    Output: Inserted data in sqlite3 DB `fund_position` table

3. Analyse (`analytics.py`)
    - Runs SQL based analytics on 
        - Price reconciliation (available in fund level summary/symbol level breakdown)
        - Best performing fund by month
    
    Output: Analysis results exported to analytics directory
    ```data/analytics/<analysis_name>.csv```


### Detailed Directory Breakdown
#### `main.py`
Main entrypoint for the project to perform all operations (initialise, extract, load, analyse) run via command line.

#### `src/`
```
├───src
│   │   analytics.py
│   │   extract_data.py
│   │   init_tables.py
│   │   load_data.py
│   │   __init__.py
```
Each file in this directory is an abstraction of each step in the ETL. 
> [!NOTE]
> - This layer of abstraction is considered with the potential of adding orchestraction layer, and each DAG is able to attach to each operation independently.
> - E.g. Four Airflow DAGs, each PythonOperator attached to `init_tables.py`, `extract_data.py`, `load_data.py` and `analytics.py`.

#### `data/`
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
- `data/raw/`: First landing directory of raw fund CSVs.
- `data/staging/`: Staged files post extaction and processing from extract step. Contains subdirectories partitioned by date in YYYY-MM-DD (for future efficient loading from stage to DB).
- `data/analytics/`: Exports of reconciliation analysis between funds vs reference price (summary and symbol level available) and analysis of monthly best performing funds.

#### `sql/`
```
├───sql
│   │  best-performing-fund.sql
│   │  fund-position.sql
│   │  master-reference-sql.sql
│   │  reconciliation-query-breakdown.sql
│   │  reconciliation-query-summary.sql
```
Contains sql scripts for execution. Includes DDL for table initiation, as well as select queries for analytics step.

#### `utils/`
```
└───utils
    │   db_utils.py
    │   file_utils.py
    │   log_utils.py
    │   metadata_utils.py
    │   __init__.py
```
Common utility scripts used and imported from other scripts in this repository, such as DB connection utilities.

#### `test/`
```
├───test
│   │   test_analyse.py
│   │   test_extract.py
│   │   test_load.py
│   │   __init__.py
```
Directory containing unit testing for key functions and components of the repository. Namely load, extract and analyse.

#### `configs/`
```
├───config
│   │   analytics_configs.py
│   │   db_configs.py
│   │   file_configs.py
│   │   __init__.py
```
Directory containing configuration details such as file naming conventions, database reference scripts for DDL etc.


## Assumptions/Scope of take-home submission

1. Incoming Funds Data 
    - Arrives monthly and consistent as CSV file format.
    - File structure and naming are consistent across months.
    - Filenames will always have EOM date (with year, month, day details) and fund name.
    - For a given month, each fund only has one csv file. Files are not resent or duped.

2. Reference data
    - All insturments and symbols in incoming data are available in master reference dataset.
    - Master reference dataset is assumed to be clean and complete for pricing.

3. Fund coverage
    - Submission covers the scope for N datasets. 
    - Logic to handle onboarding of new funds beyond the 10 funds in this submission is out of scope.

4. Pricing/Valuation
    - Utilising most recent available price data, prior to the specified date should there be gaps.

5. Execution of the solution
    - Assumed to be run locally without orchestration/scheduling or production deployments.

## Potential Future Enhancements/Known Gaps
1. Extract
    - Logic to skip erronous file while continuing to extract others.
    - Incremental ingestion and handling.
    - Produce extract report/extract history.
2. Load
    - Upsert logic to update previously loaded records that changed, insert new records, while ignore unchanged records. (currently appends only  logic. Duplicated records expected if identical run)
    - Load by specific date partitions.
3. Analyse
    - Enhancing to use pandas for further post-SQL query processing.
4. Others
    - Logic to continue subsequent steps when previous steps are failing in ```main.py```.
    - Option to run only certain operations while not others (e.g. only load) - potentially with command line arguments in main().
    - Unit testing coverage on data quality/query related logic (e.g.results from analytics).