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

The following ETL process will be triggered upon invocation of main.py
- Initialise a sqlite3 DB with tables (reference and fund postion) initialised.
- Extract raw funds CSV to staging directory, with enrichment of metadata (fundname and date) in content of CSV.
- Load all CSV files from staging area to sqlite3 DB into fund_position table
- Perform fund reconciliation and best performing fund analyses, exporting the results as CSV.


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


## Gaps to productionise from submission
1. Incremental ingestion and handling
2. Orchestration
3. Data Quality management
4. Table/query/view performance considerations (e.g. indexing)